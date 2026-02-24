# Pseudocode Interpreter
This is a fully-working interpreter that allows students to run IGCSE Pseudocode, a language which is used in IGCSE Computer Science but has no formal interpreter / compiler available.

**Date created:**May 2024

## How to run the program

1. *Install Python if it is not present in your computer.* The version I have on my machine is python 3.11 available to download [here](https://www.python.org/downloads/release/python-3110/). Other versions of python could work, but I haven't tested it out yet.

2. *Install files uploaded here,* specifically decoder.py, settings.json at least (the program will not run without settings.json)

3. *Create a file with the name 'code.txt'.*

4. Write the code using official pseudocode syntax, as in the [IGCSE Computer Science syllabus of 2023 - 2028](https://www.cambridgeinternational.org/Images/697167-2026-2028-syllabus.pdf#page=35). There are reference code examples available in the codeExamples folder in this repository.

5. *Once you're done, check settings.json to ensure the settings are as required for your program:* Note that in the settings.json file, the assignment operator is called a delimiter. This is an issue and I will fix this in a future build.

6. *Open decoder.py and it will run the program.*

## Images

Execution of the random fairness tester program (with debugging active): For harder, resource-intensive programs
![Execution of the random fairness tester program (with debugging active): For harder, resource-intensive programs](image-1.png)

![Execution of a random number game - this is the typical execution speed for a longer ](image-2.png)


## OVERVIEW OF BUILD
### Why I Made This
During the beginning of A Levels, I was tutoring some students for IGCSE computer science, who struggled with writing code usually. For the exams, we had the option to write the exam in a regular language (such as python), or pseudocode, which had a specific syntax and format, that all students had to learn, since we NEEDED to know how to write in pseudocode.

Most students pick to write in pseudocode, rather than learning two different languages. However, this proves to be a challenge for multiple students as it is quite hard to practice coding, when you get no feedback. As a result, it's hard to really learn coding for most students since this is the first language most students pick up. And, there is no better joy than seeing your code ACTUALLY run in real time.

As a result, I was inspired to create my own interpreter, implementing most core features, within a few days or so, save for bug fixing.

However, during the process of creation, I realised that others had made it too, and published similar programs. I decided to take a look at them. But, most of them weren't up to the standard I wanted. Few actually ran properly, with them usually missing things like library functions, and most were web builds. As a result, few actually had options to practice file handling and the like. Along with that, most had a plethora of ads and microtransactions, and required a long time to load & run, and since they were web builds, none could be run offline. On top of that, they struggled to run code at a decent time, especially for more taxing programs. Furthermore, few had customisable options for the programs, such as changing the delimiters, or any debugging options. And on top of that, some used completely wrong syntax, compared to IGCSE, so students would get confused with varying syntax.

I made this program to address all the aforementioned issues and make an interpreter that could be run locally, free for all students. While I made this program roughly two years ago, I did the bug fixings and optimisations over the past few months, after I was finished with school since it was quite hard to find the time to finish this project.

### About IGCSE Pseudocode

IGCSE pseudocode is an program with complexity between python and C. While it is more rigorous than python, which mandatory declaration of variables with type (you can't store any value in any variable, like python), ENDIF statements, etc. It is still an easier language compared to C, with no pointers, or other complicated functions. 

It's a good language for beginners to learn programming in, since it prevents formation of bad habits in programming, such as having a variable that stores a number once, an array once, etc. without being too complicated syntax wise, like c, especially for functions like string handlling and the like.

### How the program works

The program takes the code written into code.txt, and interprets it, line by line, with the way the code is executed, handled by the settings selected in settings.json. It mostly uses string handling to determine which operation to run, what are the parameters, etc.

The program has mainly two key backbone functions - getVal, and execCode. 

getVal takes a value, a function, a variable/array/constant, or an expression, in string format and returns a processed, operatable value. This is useful to find, say, the status of a condition(Value >= TRUE OR x < y>), or to compute the value of an expression (56 / 5).

execCode takes in code and executes it line by line. This is used in procedure / function handling as well, or in loops to run a code a number of times.

Apart from this, errorHandle returns errors, getType gets the type of a pure data, say, a integer value, and returns the type, which is used for data validation. The other functions in the program, are mainly text handling / other code that gets called multiple times within the program, so I made functions for better readability.

### Optimisations

Optimisation is my weak point - while I can come up with logic on my own, without relying on stack overflow (as I did with this program and the other programs I created), and debug code, I'm quite unfamiliar with optimising code, and I usually just go with the logic of rewrite a different logic system till I get a decent speed.

However, with this project being that complex, this was not possible. I had delayed on optimisations, since 5ms while slow, for hello world programs and simple programs compared to python and formal languages, I reasoned that it was fast enough to not be particularly noticable to people - if a program could run in under 1 second, it would look fast. So my goal was to get any program to be run at a speed which looked fast.

During my bug-testing phase, where I was going through code written in IGCSE papers on 2023 October, i noticed a fairness tester for random number generators as one program students were expected, however, this was when the limitations of the code began to show up. Said code did the following - generate 100000 numbers in the range of 0-10 via a random function, andn then count the frequency of each number generated. 

This program took around 10min to complete even just the first stage, so I knew I had to optimise the code. This took... more than.. two weeks, especially since, again, I didn't even know what I was doing at first.

Luckily, I did have a few ideas, since after practicing coding for the past few years, I knew this code, which I wrote a few months after my O levels, wasn't the best, using really time consuming strategies, such as appending blank values to arrays than using list comprehensions, etc, or going through characters line ny line in the replace and bracketExcluded split functions.

So I began by rewriting the code for these programs, changing anything that declared lists and values without list comprehension, or used list.pop functions, with list comprehensions, since they would be faster.

On top of that, I modified statements with copy.deepcopy only as required. Copy.deepcopy is needed in some cases, say, to create a copy of a 2d array, which doesnt change values of the other array the values were copied from? It's an issue in python, basically, and this is the one way to fix it. 

I also changed the removeSpace function, firstSpecialChar, bracketExludedSplit, checkClosingBracket, to be more effecient, say, by skipping checking the position of the first special character if it is only an alphanumeric string, or just returning a value using the .split function in python if there's no brackets to worry about.

This brought the runtime down from 10min for the first part of the code, to generate 100000 numbers, down to 2min, but i was still unsatisfied by the speed. I knew since this was the first time i'd actually made a compiler and my logic, isnt.. standard per se, it wouldn't be a good runtime, but I still wanted to try better,

I changed getVal if statement orders, so it checked first for non-taxing cunditions, like if a value was only a variable, or an integer, before checking for things like if something was an expression, which required it to go through, 20 different symbols and see if they exist or not in the expression, and aren't just an expression of an array index, like say, array[9+5]. This is still considered an array call, not an evaluation call and would be handled differently.

With that, I could get runtime to 1min 45s. After that, I changed the function for checking arrays/functions to eliminate time constraints, such as checking if it was NOT an expression there, when we knew it couldn't be one with an easier expression, or so.

On top of that, I added a dictionary containing all the commonly used list of operators used for this evaluation checking, so that the list comprehesions only happened once and could be called any time. I addes a function that specifically checked for operators in the expression, which weren't in an array or function, etc. which all brought the time to run the first statement to rougnly 1min.

I was estatic that the program improved the run time so much, but still, the final program still took around 3-4min to run completely. So for my final optimisation, I added cache functions for evaluations and functions, which cached the variables that had to be checked, any important conditions, etc. for evaluations and function calls which were done multiple times in say, loops.

All of this brought the final program runtime to 30s - 1min 45s for this random fairness tester, which was good. I also changed it so the commonly referred lists were changed to tuples, since I knew tuples were generally faster than lists. With this change, most simple programs run in less than 0.05ms, and even the most taxing program i could find on an IGCSE paper (this random fairness tester) only takes 12s - 1min 15s to run on an average computer. It seems still quite inconsistent on different systems - some systems can run it in 12s, some can run it in 1min 30s, and it seems to be affected by thermal throttling, and other CPU factors.

### New concepts I learnt while making the program

This was the first time I'd made a serious attempt at a compiler. My first "compiler" was for mainly esoteric languages, which were very easy to create, but here, I had to implement a variety of features to prevent people from breaking the program by say, using brackets, using multiple spaces, etc. So this was a good experience to help me familiarise myself with two key concepts:

1. Recursive functions: Before this program, I didn't know much about recursive functions, and this helped me get more familiar with the idea of them, and how to use them, especially since i had to somewhat see that my compiler could also handle them.

2. Optimisation tricks: I learnt a wide variety of optimisation strategies as i mentioned before, which are bound to be useful in future implementations.

## Future implementations / known bugs im working on fixing
### BUGS:
- *Error handling issues:* While the code works mostly fine with code in the proper syntax, it may exhibit strange behavior or just give a vague UNRECOGNISED STATEMENT, or just crash with no explanations for code with clear errors. While I'd started on error handling, it's still not fully complete, especially for errors in recursive procedures or within a function so some bugs are expected in that case, during error handling.

### Future implementations:
I plan on making this program more versatile than it is currently, since pseudocode, usually may be more freely written by some students. So for relaxed coding, and to change behavior of pseudocode, I plan on adding multiple settings to change the behavior of the interpreter, such as:

- *Multiple assignment operators:* This allows students to switch between delimiters. While it's not.. ideal - consistency is important in languages, it's useful for students who may use arrows or equal signs inconsistently in the same code.

- *Equal sign or <- as an assignment operator:* Equal signs will be more familiar to students who use python, however, the current compiler will run into issues since equal signs are considered to be on par to the expression equal sign. In python, this is gotten away using  == to check for equality, but there's no feature like that as of now.

- *Auto-detect assignment operators / other settings:* I know few students would actually play around with the settings, so to make it easier for students, I will be adding the option to detect any settings that could be used by the student, such as the type of assignment operator they've used for the code, etc.

- *Run-time debugging:* Right now, the only debugging that can be done outside running the program in vscode directly and using its debugger on the interpreter, is displaying variables in the end. I will be implementing breakpoints so students can see what happens to specific variables at specific points in the code for easier use.

- *Syntax-highlighting:* This should be creating a vs code extension, but since i'm unfamiliar with node.js, I'll be implementing this in a future build later, since this will be useful for students for legibility purposes.

- *Case-insensitive variables:* The default IGCSE pseudocode does not make a distinction between variables x and X, which is an atypical behavior compared to other languages, which made me hesistant on implementing it, but I will add the setting later.

- *PRINT instead of OUTPUT and other syntax formatting options:* Some students may be more familiar with using PRINT, rather than output, so I'll be adding the option to change which syntax you can use for the programs - again, not a typical behavior for IGCSE pseudocode, but for a customisable experience, I will add features such as this, to allow students to be more comfortable with coding, especially if they're not using the official pseudocode guidelines.

- *Different intendation options:* The current code uses tab intendation, or four space intendations. While official guidelines suggest 2 space indentation, I'm not fond of space indentations, so I didn't implement it. Furthermore, I know of some students who DONT use indentations, so i'll add a setting that allows programs to be run even without correct indentation.

- *No endif statements:* Again, this is a quality-of-life- fix since during coding, you may want to not write ENDWHILE, etc in your code. Assuming other settings are fine, I will write a fix for this so students can run a program without end statements, should they wish.

- *Output modifications:* I will add settings that allows students to customise how the OUTPUT operation behaves, such as skipping newlines without it being explicity added in OUTPUT statements, or adding a whitespace by default when strings are seperated by commas or not.

- *No declaration/mutable declaration:* Again, some students may not like rigid rules in pseudocode, and may be more used to not having to declare variables, or their type, or array lengths, so for them, I will be adding settings that allow them to do so if they want, making it easier for students to program.

- *3D+ arrays, dictionaries, and other programming constants:* It is of no doubt that certain features are lacking in pseudocode, such as more complex variable types, and as such, I will be adding settings that you can turn on to add such complex variable types, with a syntax I feel would be similar to other syntax in pseudocode, but isn't officially backed by IGCSE, for more complicated projects.

- *Library values:* There are two types of libraries I wish to add, one being library values, such as names, etc. that students can auto-fill arrays with, sinc ein most IGCSE code cases, it is assumed arrays are already filled. This can be complicated to bug test, since it would require filling multiple arrays manually, so I will be adding libraries for students to auto fill arrays in such cases.

- *Libraries for operations:* This includes things like GUI handling, color customisations in the terminal, sound handling, json handling, some typical library functions such as .split and .replace written in python, for faster access, and to allow more complex programs to be run.

- *Compiling / reverse compiling:* I will be adding a setting to convert pseudocode into another commonly used beginner language, such as C, C++, javascript, java, or bash, or python and a setting to convert a program of any of the aforementioned types to a program with the same function in pseudocode. This will also include the ability to compile pseudocode to an exe. 

---

If you have any bugs, suggestions or any questions regarding this program, send an email to me on pixiepowers351@gmail.com with a copy of the files in the compiler folder, specifically the code.txt file and the settings.json file, and i'll be sure to respond in a few days at least, and try to fix it in a week or so. 

Or you could alternatively post the issue on github, but i'm less familiar with that - it's my first time using github for publishing code, but I'll be sure to check any issues posted like that too!