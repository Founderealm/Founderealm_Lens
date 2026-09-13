package main

import (
	"fmt"
)

const Alpha = "hello"

func Delta() string {
	return fmt.Sprintf("Value: %s", Alpha)
}

func helper() string {
	return Delta()
}
