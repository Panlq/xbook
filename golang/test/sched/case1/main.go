package main

import (
	"fmt"
)

func main() {
	go func(n int) {
		for {
			n++
			fmt.Println(n)
		}
	}(0)

	for {

	}
}
