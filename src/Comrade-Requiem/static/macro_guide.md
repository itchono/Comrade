Macros are a way to execute instructions whenever someone types a specific phrase in chat.

__Format__
Each line of the macro is executed as a separate instruction.

There are special instructions that can be used to control the execution of the macro.

__Saying a Message__

Any line that does not have a special instruction will just be sent as a message.
```
hello
goodbye
```

__Executing a Command__

Use the `$run` instruction to execute a command.

Separate commands and arguments using a `:` (colon). This is because some commands require multiple arguments.
```
$run echo: hello: <@709953060146905098>
```

__Randomly Picking an Instruction__

Use the `$random` instruction to pick from a random list of instructions to execute.

A single instruction between `$random` and `$endrandom` will be executed randomly.

```
$random
It is cloudy today.
It is sunny today.
It is raining today.
$endrandom
```

__Conditionals__

Use the `$if` instruction to execute a command if a condition is met.

Use the `$else` instruction to execute a command if the condition is not met.

Always terminate a conditional with an `$endif` instruction.

```
$if ${ping} == <@709953060146905098>
hello <@709953060146905098>
$else
I do not know you yet, nice to meet you.
$endif
```

__Substitutions__

You can use the following substitutions to get contextual information based on the message. These might be useful for commands and conditionals.

```
${author}: username of the person calling the macro
${channel}: name of the channel the macro was called in
${ping}: @mention of the person calling the macro
${channelping} : #mention of the channel the macro was called in
${arg}: the argument passed to the macro
```

__Arguments__

Macros will accept a single argument passed in the message. You can access this argument using the `${arg}` substitution.

If your macro is called `wave`, and someone types `wave at me`, the argument will be `at me`.
