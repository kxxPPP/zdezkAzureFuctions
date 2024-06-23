# zdezkAzureFuctions

## What is this?

This is a sepperate repository for the azureFunctions I use to run serverless processes on my website.


Developement workflow:

1. Create a function in the main repository
2. Clone the function in the test repository
3. Clone the test repository to a local directory
4. Develope and test changes by locally testing the azure functions with azure functions core tools + VScode
5. Delete the local testing logic from the function after it is confirmed to be working
6. Push the new function to the test branch of the repository and create the new function in azure
