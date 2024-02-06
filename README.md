# github-workflow-build-terraform-interface

This is a beta release of a terraform interface builder github action. As of now there are no tests, and
it has only been tested on Azure's storage account backend and AWS's S3/Dynamo DB backend. It scans a terraform template then creates an interface module that 
calls the remote state of a terraform environment and surfaces its outputs.

## How it works

1) on push, the action scans the repo for the a file called `build-interface.here`
2) once the action finds the file it creates a folder called `interface` in. It then creates three files in the folder:
    1) `variables.tf` - as of now, this is 100% hardcoded. And just asks for a workspace name.
    2) `outputs.tf` - the outputs of the terraform template's state proxied through the interface
    3) `state.tf` - this defines the terraform remote state data source

The files `variables.tf`, `state.tf` and `outputs.tf` are 100% machine generated. If you put any code in them, it will 
be clobbered automatically. I highly suggest that if you need to tweek the interface, you create additional files and do 
it there.
