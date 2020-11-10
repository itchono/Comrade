package main

import (
	"encoding/csv"
	"fmt"
	"strings"
)

// CommandReader reads a command given an input string, and splits it into its fields.
func CommandReader(s string) []string {
	// Split string

	r := csv.NewReader(strings.NewReader(s))
	r.Comma = ' ' // space
	fields, err := r.Read()

	if err != nil {
		fmt.Println(err)
		return []string{} // return null
	}

	return fields
}
