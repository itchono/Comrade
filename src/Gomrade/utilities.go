package main

import (
	"encoding/csv"
	"fmt"
	"strconv"
	"strings"
)

// CommandReader reads a command given an input string, and splits it into its fields.
func CommandReader(s string) []string {
	// check prefix
	if s[:len(prefix)] != prefix {
		return []string{} // return null
	}

	s = s[len(prefix):] // drop prefix

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

// isInt returns true if a string is numeric
func isInt(s string) bool {
	_, err := strconv.ParseInt(s, 10, 64)
	return err == nil
}
