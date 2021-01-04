package main

import (
	"context"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"os/signal"
	"strings"
	"syscall"
	"time"

	"github.com/bwmarrin/discordgo"
	"github.com/joho/godotenv"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

// Variables (global)
var (
	Token     string
	MDB       string
	client    *mongo.Client
	comradeDB *mongo.Database
)

// init is called before main
func init() {

	if err := godotenv.Load(); err != nil {
		fmt.Println("No .env file found")
	}
	Token, _ = os.LookupEnv("TOKEN")
	MDB, _ = os.LookupEnv("MONGOKEY")
}

func main() {
	// MongoDB init
	client, _ = mongo.NewClient(options.Client().ApplyURI(MDB))
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	_ = client.Connect(ctx)
	comradeDB = client.Database("comradeDB")

	// Create a new Discord session using the provided login information.
	dg, err := discordgo.New("Bot " + Token)
	if err != nil {
		fmt.Println("error creating Discord session,", err)
		return
	}

	dg.Identify.Intents = discordgo.MakeIntent(discordgo.IntentsAll)

	dg.AddHandler(messageCreate)
	dg.AddHandler(messageReactionAdd)

	// START BOT
	// Open a websocket connection to Discord and begin listening.
	err = dg.Open()
	if err != nil {
		fmt.Println("error opening connection,", err)
		return
	}

	// SERVER
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintf(w, "Hello!")
	})

	fmt.Printf("Starting server at port 8080\n")
	fmt.Println("Bot is now running.  Press CTRL-C to exit.")
	if err := http.ListenAndServe(":8080", nil); err != nil {
		log.Fatal(err)
	}

	doEvery(5*time.Second, helloworld)
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

	if strings.ToLower(m.Content) == "hello ground dragon" {
		s.ChannelMessageSend(m.ChannelID, "hello")

	} else if strings.HasPrefix(strings.ToLower(m.Content), "!") {
		success := Command(s, m)
		if success != 0 {
			fmt.Println("COMMAND ERROR")
		}
	}

	Emote(s, m, comradeDB.Collection("Emotes"))
}

func messageReactionAdd(s *discordgo.Session, m *discordgo.MessageReactionAdd) {
	r := m.Emoji.Name

	ch, _ := s.Channel(m.ChannelID)

	if ch != nil {

		fmt.Printf("Emote %s detected in channel %s\n", r, ch.Name)

	}
}

func doEvery(d time.Duration, f func(time.Time)) {
	for x := range time.Tick(d) {
		f(x)
	}
}

func helloworld(t time.Time) {
	resp, err := http.Get("https://GroundDragon.itchono.repl.co")

	if err != nil {
		log.Fatalln(err)
	}

	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)

	if err != nil {
		log.Fatalln(err)
	}

	log.Println(string(body))

	fmt.Printf("%v: Executed Ping\n", t)
}
