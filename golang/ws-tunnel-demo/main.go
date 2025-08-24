package main

import (
	"bytes"
	"encoding/json"
	"io"
	"log"
	"net"
	"net/http"
	"os"
	"sync"

	"github.com/gorilla/websocket"
)

var upgrader = websocket.Upgrader{
	ReadBufferSize:  1024,
	WriteBufferSize: 1024,
	CheckOrigin: func(r *http.Request) bool {
		return true
	},
}

// AgentManager 管理所有连接的Agent
type AgentManager struct {
	agents map[string]*websocket.Conn
	mu     sync.RWMutex
}

func NewAgentManager() *AgentManager {
	return &AgentManager{
		agents: make(map[string]*websocket.Conn),
	}
}

func (am *AgentManager) AddAgent(id string, conn *websocket.Conn) {
	am.mu.Lock()
	defer am.mu.Unlock()
	am.agents[id] = conn
	log.Printf("Agent %s connected", id)
}

func (am *AgentManager) RemoveAgent(id string) {
	am.mu.Lock()
	defer am.mu.Unlock()
	if _, ok := am.agents[id]; ok {
		delete(am.agents, id)
		log.Printf("Agent %s disconnected", id)
	}
}

func (am *AgentManager) GetAgent(id string) (*websocket.Conn, bool) {
	am.mu.RLock()
	defer am.mu.RUnlock()
	conn, ok := am.agents[id]
	return conn, ok
}

// ProxyRequest 定义代理请求结构
type ProxyRequest struct {
	TargetAddr string            `json:"target_addr"`
	Method     string            `json:"method"`
	Path       string            `json:"path"`
	Headers    map[string]string `json:"headers"`
	Body       []byte            `json:"body"`
}

// ProxyResponse 定义代理响应结构
type ProxyResponse struct {
	Status  int               `json:"status"`
	Headers map[string]string `json:"headers"`
	Body    []byte            `json:"body"`
}

var agentManager = NewAgentManager()

// Hub 处理WebSocket连接
func handleAgentConnection(w http.ResponseWriter, r *http.Request) {
	agentID := r.URL.Query().Get("agent_id")
	if agentID == "" {
		http.Error(w, "agent_id is required", http.StatusBadRequest)
		return
	}

	wsConn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Printf("WebSocket upgrade error: %v", err)
		return
	}
	defer func() {
		wsConn.Close()
		agentManager.RemoveAgent(agentID)
	}()

	agentManager.AddAgent(agentID, wsConn)

	// 保持连接
	for {
		_, _, err := wsConn.ReadMessage()
		if err != nil {
			log.Printf("Agent %s connection error: %v", agentID, err)
			break
		}
	}
}

// 处理代理请求
func handleProxyRequest(w http.ResponseWriter, r *http.Request) {
	agentID := r.Header.Get("X-Agent-ID")
	if agentID == "" {
		http.Error(w, "X-Agent-ID header is required", http.StatusBadRequest)
		return
	}

	// 解析请求
	proxyReq := ProxyRequest{
		TargetAddr: r.Header.Get("X-Target-Addr"),
		Method:     r.Method,
		Path:       r.URL.Path,
		Headers:    make(map[string]string),
		Body:       []byte{},
	}

	if proxyReq.TargetAddr == "" {
		http.Error(w, "X-Target-Addr header is required", http.StatusBadRequest)
		return
	}

	// 复制headers
	for k, v := range r.Header {
		if len(v) > 0 {
			proxyReq.Headers[k] = v[0]
		}
	}

	// 读取body
	if r.Body != nil {
		body, err := io.ReadAll(r.Body)
		if err != nil {
			http.Error(w, "Failed to read request body", http.StatusInternalServerError)
			return
		}
		proxyReq.Body = body
	}

	// 获取agent连接
	agentConn, ok := agentManager.GetAgent(agentID)
	if !ok {
		http.Error(w, "Agent not found", http.StatusNotFound)
		return
	}

	// 发送请求到agent
	reqBytes, err := json.Marshal(proxyReq)
	if err != nil {
		http.Error(w, "Failed to marshal request", http.StatusInternalServerError)
		return
	}

	if err := agentConn.WriteMessage(websocket.BinaryMessage, reqBytes); err != nil {
		http.Error(w, "Failed to send request to agent", http.StatusInternalServerError)
		return
	}

	// 等待响应
	_, respBytes, err := agentConn.ReadMessage()
	if err != nil {
		http.Error(w, "Failed to read response from agent", http.StatusInternalServerError)
		return
	}

	var proxyResp ProxyResponse
	if err := json.Unmarshal(respBytes, &proxyResp); err != nil {
		http.Error(w, "Failed to parse response from agent", http.StatusInternalServerError)
		return
	}

	// 写回响应
	for k, v := range proxyResp.Headers {
		w.Header().Set(k, v)
	}
	w.WriteHeader(proxyResp.Status)
	w.Write(proxyResp.Body)
}

// Agent实现
func runAgent(wsURL, agentID string) {
	headers := http.Header{}
	wsConn, _, err := websocket.DefaultDialer.Dial(wsURL+"?agent_id="+agentID, headers)
	if err != nil {
		log.Fatalf("Failed to connect to WebSocket: %v", err)
	}
	defer wsConn.Close()

	log.Printf("Agent %s connected to hub", agentID)

	for {
		_, message, err := wsConn.ReadMessage()
		if err != nil {
			log.Printf("Read error: %v", err)
			break
		}

		var proxyReq ProxyRequest
		if err := json.Unmarshal(message, &proxyReq); err != nil {
			log.Printf("Failed to parse request: %v", err)
			continue
		}

		// 执行代理请求
		resp, err := executeProxyRequest(&proxyReq)
		if err != nil {
			log.Printf("Failed to execute request: %v", err)
			continue
		}

		// 发送响应回hub
		respBytes, err := json.Marshal(resp)
		if err != nil {
			log.Printf("Failed to marshal response: %v", err)
			continue
		}

		if err := wsConn.WriteMessage(websocket.BinaryMessage, respBytes); err != nil {
			log.Printf("Write error: %v", err)
			break
		}
	}
}

func executeProxyRequest(req *ProxyRequest) (*ProxyResponse, error) {
	// 建立到目标地址的连接
	conn, err := net.Dial("tcp", req.TargetAddr)
	if err != nil {
		return nil, err
	}
	defer conn.Close()

	// 构造HTTP请求
	httpReq := buildHTTPRequest(req)

	// 发送请求
	if _, err := conn.Write(httpReq); err != nil {
		return nil, err
	}

	// 读取响应
	buf := make([]byte, 4096)
	n, err := conn.Read(buf)
	if err != nil && err != io.EOF {
		return nil, err
	}

	// 解析HTTP响应
	return parseHTTPResponse(buf[:n])
}

func buildHTTPRequest(req *ProxyRequest) []byte {
	var buffer bytes.Buffer

	// 请求行
	buffer.WriteString(req.Method + " " + req.Path + " HTTP/1.1\r\n")

	// 请求头
	for k, v := range req.Headers {
		buffer.WriteString(k + ": " + v + "\r\n")
	}
	buffer.WriteString("\r\n")

	// 请求体
	if len(req.Body) > 0 {
		buffer.Write(req.Body)
	}

	return buffer.Bytes()
}

func parseHTTPResponse(data []byte) (*ProxyResponse, error) {
	resp := &ProxyResponse{
		Headers: make(map[string]string),
	}

	// 简单解析HTTP响应
	lines := bytes.Split(data, []byte("\r\n"))
	if len(lines) < 1 {
		return nil, io.EOF
	}

	// 解析状态行
	if len(lines[0]) > 0 {
		parts := bytes.SplitN(lines[0], []byte(" "), 3)
		if len(parts) >= 2 {
			resp.Status = bytesToInt(parts[1])
		}
	}

	// 解析headers
	bodyStart := 0
	for i := 1; i < len(lines); i++ {
		if len(lines[i]) == 0 {
			bodyStart = i + 1
			break
		}
		parts := bytes.SplitN(lines[i], []byte(": "), 2)
		if len(parts) == 2 {
			resp.Headers[string(parts[0])] = string(parts[1])
		}
	}

	// 合并body
	if bodyStart < len(lines) {
		var body []byte
		for i := bodyStart; i < len(lines); i++ {
			body = append(body, lines[i]...)
			if i < len(lines)-1 {
				body = append(body, '\n')
			}
		}
		resp.Body = body
	}

	return resp, nil
}

func bytesToInt(b []byte) int {
	var n int
	for _, ch := range b {
		ch -= '0'
		if ch > 9 {
			break
		}
		n = n*10 + int(ch)
	}
	return n
}

func main() {
	if len(os.Args) > 1 && os.Args[1] == "agent" {
		if len(os.Args) < 3 {
			log.Fatal("Usage: agent <ws-url> <agent-id>")
		}
		wsURL := os.Args[2]
		agentID := os.Args[3]
		runAgent(wsURL, agentID)
		return
	}

	// 运行Hub
	http.HandleFunc("/connect", handleAgentConnection)
	http.HandleFunc("/proxy", handleProxyRequest)

	port := "8081"
	log.Printf("Hub listening on :%s", port)
	log.Fatal(http.ListenAndServe(":"+port, nil))
}
