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

