package main

import (
	"fmt"
	"strings"

	"github.com/bwmarrin/discordgo"
)

// Tunnel interprets a discord message event and executes the corresponding command
func Tunnel(s *discordgo.Session, m *discordgo.MessageCreate) int {
	// returns -1 in case of error
	if m.GuildID == RELAYID && strings.HasPrefix(m.Content, "<%GO>") {

		fmt.Println("Message Received: " + m.Content)
	}
	return 0
}

// Relay sends a message to the relay server
func Relay(s *discordgo.Session, message string) {
	s.ChannelMessageSend(relayChannel.ID, "<%PY>"+message)

}
