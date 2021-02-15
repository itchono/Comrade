package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"strings"
	"syscall"
	"time"

	"github.com/bwmarrin/discordgo"
	"github.com/joho/godotenv"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

// Variables (global)
var (
	Token        string
	MDB          string
	client       *mongo.Client
	comradeDB    *mongo.Database
	prefix       string
	RELAYID      string
	relayChannel *discordgo.Channel
)

// init is called before main
func init() {
	prefix = "$h "
	if err := godotenv.Load(); err != nil {
		fmt.Println("No .env file found")
	}
	Token, _ = os.LookupEnv("TOKEN")
	MDB, _ = os.LookupEnv("MONGOKEY")
	RELAYID, _ = os.LookupEnv("RELAYID")
}

func main() {
	// MongoDB init
	client, _ = mongo.NewClient(options.Client().ApplyURI(MDB))
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	_ = client.Connect(ctx)

	dblist, _ := client.ListDatabases(ctx, bson.D{})

	comradeDB = client.Database(dblist.Databases[0].Name)

	// Create a new Discord session using the provided login information.
	dg, err := discordgo.New("Bot " + Token)
	if err != nil {
		fmt.Println("error creating Discord session,", err)
		return
	}
	dg.Identify.Intents = discordgo.MakeIntent(discordgo.IntentsAllWithoutPrivileged)
	dg.StateEnabled = true
	dg.AddHandler(messageCreate)
	dg.AddHandler(ready)

	// START BOT
	// Open a websocket connection to Discord and begin listening.
	err = dg.Open()
	if err != nil {
		fmt.Println("error opening connection,", err)
		return
	}

	// Post-init stuff
	dg.UpdateGameStatus(0, "["+prefix+"] Accelerating Communism")

	// SERVER
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintf(w, "Gomrade is online.")
	})

	if err := http.ListenAndServe(":8080", nil); err != nil {
		log.Fatal(err)
	}
	// Wait here until CTRL-C or other term signal is received.
	sc := make(chan os.Signal, 1)
	signal.Notify(sc, syscall.SIGINT, syscall.SIGTERM, os.Interrupt, os.Kill)
	<-sc

	// Cleanly close down the Discord session.
	dg.Close()
}

// This function will be called (due to AddHandler above) every time a new
// message is created on any channel that the authenticated bot has access to.
func messageCreate(s *discordgo.Session, m *discordgo.MessageCreate) {

	// Ignore all messages created by the bot itself
	// This isn't required in this specific example but it's a good practice.
	if m.Author.ID == s.State.User.ID {
		return
	}

	// Command Handler
	if strings.ToLower(m.Content) == "hello ground dragon" {
		s.ChannelMessageSend(m.ChannelID, "hello")

	} else if strings.HasPrefix(strings.ToLower(m.Content), prefix) {
		success := NSFWCommand(s, m)
		if success != 0 {
			fmt.Println("COMMAND ERROR")
		}
	}
	// Message Handlers
	NSFWHandler(s, m)
	Emote(s, m, comradeDB.Collection("Emotes"))
	Tunnel(s, m)
}

// This function will be called (due to AddHandler above) when the bot receives
// the "ready" event from Discord.
func ready(s *discordgo.Session, event *discordgo.Ready) {
	channels, _ := s.GuildChannels(RELAYID)

	for _, channel := range channels {
		if channel.Name == "relay" {
			relayChannel = channel
		}
	}

	if relayChannel == nil {
		fmt.Println("RELAY CHANNEL NOT FOUND")
	}
	fmt.Println("Bot is online. Logged in as", event.User.Username)
}
