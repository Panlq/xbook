package main

import (
	"fmt"
)

// gcshape.go
func f[T any](t T) {
	fmt.Printf("%T: %v\n", t, t)
}

type MyInt int

func main() {
	f[int](5)
	f[MyInt](10)
}
