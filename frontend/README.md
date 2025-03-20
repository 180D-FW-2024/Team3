This folder contains code that runs on Raspitouille locally; this includes Raspitouille's main software loop and its image recognition software.

Credits for the origins of code snippets can be found commented within each file.

The main software loop is designed for simplicity and encapsulation, such that rarely will a parent process need information from a child process.
Unfortunately, there are some cases where this encapsulation breaks down, but it does not cause any issues at the moment (besides the accumulation of tech debt).

Future improvements I would like to make to this area are simply the cleaning up of our software structure. As a result of not having clearly set conventions at the start of the project,
our team sometimes ended up using differing structures in our code. For example, command handler handles some commands directly, and delegates some commands to its parent script.