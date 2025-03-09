
'Snippet extractor' extract the code snippet of target function with dependencies (functions, classes, variables, imports, globals, objects). 
If there are some external dependencies which are imported from external files, it set the dependency as a target and constructing the external code snippets recursively, populating the final snippet.
( See the 'process_deps' function and test from the 'main')

Note: it tested only with functions as dependencies, no garanties for another categories of entities. Maybe should be improved.
