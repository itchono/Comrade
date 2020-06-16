# Cosmo

This is a scripting language developed in conjunction with the Comrade Discord Bot. This would allow for advanced queries and actions to be performed thus simplifying the task for the user and the administrator.

Currently implemented features:
 - Function parameters
 - Basic 4 math functions
 - Setting and Reading Variables
 - Printing
 - Iter loop
 - While loop
 - Conditionals
 - Boolean Statement
 - Calling discord functions


## Function Parameters
Every program needs to start with a list of function parameters
```
[x,y,z]
```
Make sure there are no spaces the between the values. All lists in Cosmo do not have spaces seperating the values. Cosmo is very space sensitive.

Important: All Cosmo scripts must include this section and will not run without it. In subsequent examples, _we will however omit this for the sake of simplicity_.


## Basic Math

**Addition**
ADD x y z
this statement is equivalent to saying: set x = y + z
```
ADD x 4 2 //sets x to6
```

**Subtraction**
SUB x y z
this statement is equivalent to saying: set x = y - z
e.g.
```
SUB x 4 2 //sets x to 2
```

**Multiplication**
MUL x y z
this statement is equivalent to saying: set x = y * z
e.g. 
```
MUL x 2 4 //sets x to 8
```

**Division**
DIV x y z
this statement is equivalent to saying: set x = y / z
e.g.  
```
DIV x 4 2 //sets x to 2
```


## Setting and Reading Variables

**Setting vars**
SET x y
this statement is equivalent to saying: set x = y
```
SET x 3 //sets x to 3
```

**Getting vars**
you can get the value of a var by using the `&` symbol infront of the var
```
SET x 3 
SET y &x //sets y equal to the value at x
```

this should be done when using math functions as well
```
SET x 3
SET y 5
ADD z &x &y //set z equal to the sum of the values at x and y
```


## Printing
**Printing**
PRINT x
this statement prints the value of x
```
PRINT 4 //prints 4
```
```
SET x 3
PRINT &x //prints 3
```

be careful with `&` before variables, if you miss it, the variable will be treated as a string and printed as such
```
SET x 2
PRINT x //prints x
```


## Looping
**Start Iter**
ITER i [x,y,z...]
creates variable i as placeholders for values and iterates over the following block with values x, y and z. 

Important: there cannot be any spaces in [x,y,z...] as the language uses spaces to determine the seperation of arguments and this input list is a single argument.

**End Iter**
ITEREND
outlines the end of the section that needs to be looped with the iterator

```
ITER x [1,2,3,4,5,6,7] //this loop prints out all the numbers in the list: all the numbers from 1 to 7
PRINT x 
ITEREND
```

**Start While**
WHILE <bool-stmt>
denotes the start of a while loop. It requires a boolean statement as an argument which evaluates to either true or false. Boolean statements will be covered further on in the documentation.

**WHILEEND**
denotes the end of the while loop

```
SET x 5
WHILE x > 0 //counts down from 5 until it hits 0
PRINT &x
SUB x &x 1
WHILEEND
```


## Conditionals
**Start of Conditional**
COND
A series of conditionals must first be prefaced with the keyword COND

**End of Conditional**
CONDEND
denotes the end of a series of conditionals

**Cases**
CASE <bool-stmt>
if the boolean statement is satisfied, the lines following this will be executed

```
SET x 5
COND
CASE x > 5
PRINT higher
CASE x < 5
PRINT lower
CASE x == 5
PRINT equal //this series of conditional cases will print "equal"
CONDEND
```


## Boolean Statements
**Boolean Literal**
literal = true | false
for any boolean statement, you can put directly either true or false

**Boolean Expression**
you can use any of your standard comparisons to compare two numbers or two strings
cmp = > | >= | < | <= | == | !=

Important: make sure you seperate the individual arguments with spaces


## Calling Discord Functions
**Call**
CALL <discord-function>
allows you to call a discord function with arguments from within the script

```
CALL $c avatar vdoubleu
```

# Implementation

This section gives some details into how the interpreter was constructed. 

This interpreter works in two parts, it first parses the program into an AST and then this AST is interpreted. 

## Parsing

Parsing this language is relatively easy as it relies on the fact that each line will have one command or statement. This means we can reliably just first split the language into lines for parsing. After this, we can begin to formally parse the language into an AST.

The AST is constructed via a combination of numerous nodes where each node contains all the information necessary to interpret it. Nodes in this language are modeled using python dictionaries.

Nodes in this AST are divided into two main types based on their function. Each of these are directly related to a line. Every line or node can be either a structural command or an action command. Structural commands are things like markers for loops, conditionals, etc. whereas actions are things like print, call, set, add etc. 

To determine their type, each node has the value 'type' which can either be 'Struct' or 'Action'.
```
type = Struct | Action
```

Struct or structural components are then further divided into different types of structural components using the value 'stype' which can a multitude of values. Most of the names should be self explanetory and should reference the keyword in the actual language. The only case to be aware of is 'Main' which denotes the main body of the program. It can be assumed that the entire program is wrapped within main.
```
stype = Main | Iter | While | Cond | Case 
``` 
Depending on the structural component, there will probably also be additional key value pairs which contain additional information about the structural component. 

**Iter**:
The Iter struct should look like the following:
`{"type": "Struct", "stype": "Iter", "iter": [], "var": _, "items": _}`
The 'iter' item should contain a list of the commands that need to be interpreted.
The 'var' item should contain the newly defined variable that acts as a place holder for items within the list of the iter loop.
The 'items' item should contain a list of the items that need to be iterated through.

**While**:
The While struct should look like the following:
`{"type": "Struct", "stype": "While", "while": [], "cond": _}`
The 'while' item should contain a list of the commands that need to be interpreted.
The 'cond' item should contain a boolean statement that needs to be interpreted.

**Cond**:
The cond struct should look like the following:
`{"type": "Struct", "stype": "Cond", "case": []}`
The 'case' item should contain a list of case structs that need to be interpreted.

**Case**:
The case struct should look like the following:
`{"type": "Struct", "stype": "Case", "case": [], "cond": _}`
The 'case' item should contain a list of commands that need to be interpreted.
The 'cond' item should contain a boolean statement that needs to be interpreted to determine whether the case needs to be interpreted.


Action components are also further divided into various different types of action components using the value 'atype'. These should also all be self explanetory as they correlate directly with the the command they represent in the actual language.
```
atype = Call | Print | Set | Add | Sub | Mul | Div
```

Action components all look the same:
`{"type": "Action", "atype": _, "args": []}`
Where 'atype' is one of the possible atypes and 'args' is the arguments fed into that action.


## Interpreting

The interpreter first creates a dictionary to simulate an environment where variables and their values are stored. 

The current interpreter works by recursively calling itself on its components. It first splits the main interp function into two different interp functions depending on whether it is an action or a structural component. 

The interp\_struct function is where the structural components are interpreted based on their stype.

The interp\_action function is where the action components are interpreted based on their atype.

To differentiate variables from string and the like, the ampersand symbol(&) is used. To interpret this, an interp\_atom function is called on every single value to determine if it is a variable or just a value.

The bin\_op functions is used to interpret binary operations. 

The interp\_bool function is used to interpret boolean statements.

A final interp\_call function is used to interpret any call statements that then need to be forwarded to Discord.
