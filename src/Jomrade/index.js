// Dependencies
const Discord = require('discord.js');
const ytdl = require('ytdl-core');
const fs = require('fs');
var toWav = require('audiobuffer-to-wav');
const arrayBufferToAudioBuffer = require('arraybuffer-to-audiobuffer')
const { type } = require('os');
const express = require('express');
const server = express();
server.all('/', (req, res)=>{
    res.send('Your bot is alive!')
})


function keepAlive(){
    server.listen(3000, ()=>{console.log("Server is Ready!")});
}

require('dotenv').config();

const client = new Discord.Client();

client.once("ready", () => {
  console.log("Bot is online.");
});

client.once("reconnecting", () => {
  console.log("Bot reconnecting...");
});

client.once("disconnect", () => {
  console.log("Bot has disconnected from Discord.");
});

client.on('message', (message) => {
    if (message.content.toLowerCase() === 'hello kaiba') message.reply("you're a third rate duelist with a fourth rate deck");

    else if (message.content === "*motivation") {
      voiceclip(message, "https://www.youtube.com/watch?v=2oiZ1oZBXxU")
    }
    else if (message.content === "*disgrace") {
      voiceclip(message, "https://www.youtube.com/watch?v=yau-rTqV4xQ")
    }
    else if (message.content === "*listen") {
      listen(message)
    }
    else if (message.content === "*export") {
      savefile2(message)
    }

  });

async function listen(message) {

  const voiceChannel = message.member.voice.channel;

  try {
    var connection = await voiceChannel.join();

    // Create a ReadableStream of s16le PCM audio
    const audio = connection.receiver.createStream(message.author, { mode: 'pcm' });
    audio.pipe(fs.createWriteStream('user_audio'));

  } catch (err) {
    console.log(err);
    return message.channel.send(err);
  }
    
}

function savefile(message) {
  fs.readFile("user_audio", null, (err, data) => {
    if (err) {
      console.error(err)
      return
    }

    console.log(data.length)

    var AudioContext = require('web-audio-api').AudioContext
  , context = new AudioContext()

    arrayBufferToAudioBuffer(data)
    .then(audioBuffer => {
      // do something with AudioBuffer

      var wav = toWav(audioBuffer)
      fs.writeFile("audio.wav", wav, null, function(err) {
        if (err) throw err;
    });
    })
  })
}

async function savefile2(message) {
  message.channel.send({
    files: ['./user_audio']
});
}


async function voiceclip(message, url) {

  const voiceChannel = message.member.voice.channel;

  try {
    var connection = await voiceChannel.join();
    const dispatcher = connection.play(ytdl(url))
      .on("finish", () => {voiceChannel.leave();})

  } catch (err) {
    console.log(err);
    return message.channel.send(err);
  }

}

keepAlive();
client.login(process.env.TOKEN)
