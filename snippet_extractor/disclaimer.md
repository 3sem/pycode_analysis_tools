nefanov90, 2025.

'Snippet extractor' extracts code snippet of target function with dependencies (functions, classes, variables, imports, globals, objects). 
If there are some external dependencies which are imported from external files presented in input, it sets the dependency as a target and constructs the external code snippet recursively, populating the final snippet.
( See the 'process_deps' function and test from the 'main')

Note: 

- tested only with functions as dependencies, no guaranties for another categories of entities. Maybe should be improved.
- aliasing of dependencies by 'as' should be checked more carefully
