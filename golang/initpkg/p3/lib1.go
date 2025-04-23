package p3

import (
	"fmt"

	"github/panlq/xbook/go/initpkg/trace"
)

var V1_p3 = trace.Trace("init v1_p3", 3)

var V2_p3 = trace.Trace("init v2_p3", 3)

func init() {
	fmt.Println("init func in p3")
	V1_p3 = 300
	V2_p3 = 300
}
