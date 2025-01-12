I-ALiRT Setup
=============

Secrets Manager
~~~~~~~~~

Ensure you have a secret in AWS Secrets Manager with a username and password for the Nexus repo. The secret should be named `nexus-repo` and can be created using the following command::

    aws secretsmanager create-secret --name nexus-repo --description "Credentials for Nexus Docker registry" --secret-string '{"username":"your-username", "password":"your-password"}'

Image Versioning
~~~~~~~~~
We will rely on semantic versioning for the images MAJOR.MINOR (e.g., 1.0).

- MAJOR: Major changes.
- MINOR: Minor changes.

For development we will keep the major changes at 0.

Nexus Repo
~~~~~~~~~
We will have a versioned image and latest image in the Nexus repo. The versioned image will be tagged with the version number (e.g., 1.0) and the latest image will be the same as the most recent version. The reason that we do this is to ease the ability to switch out images in ECS.

#. Check that you are not already logged in by running::

    cat ~/.docker/config.json

#. Ensure that the Nexus registry URL is not in the list of logged in registries.
#. Run the following command to login (you will be prompted for your WebIAM username and password)::

    docker login docker-registry.pdmz.lasp.colorado.edu
#.  Your `~/.docker/config.json` file should now contain a reference to the registry url.
#.  Determine the appropriate version for your image based on the semantic versioning scheme (MAJOR.MINOR).
#. Build the image and tag it with the Nexus registry URL::

    docker build -t ialirt:X.Y --rm . --no-cache

#. Tag with the Nexus registry URL::

    docker tag ialirt:X.Y docker-registry.pdmz.lasp.colorado.edu/ialirt/ialirt-<primary or secondary>:X.Y
    docker tag ialirt:X.Y docker-registry.pdmz.lasp.colorado.edu/ialirt/ialirt-<primary or secondary>:latest

#. Push the image::

    docker push docker-registry.pdmz.lasp.colorado.edu/ialirt/ialirt-<primary or secondary>:X.Y
    docker push docker-registry.pdmz.lasp.colorado.edu/ialirt/ialirt-<primary or secondary>:latest
#. Images may be viewed on the Nexus website: https://artifacts.pdmz.lasp.colorado.edu
#. To verify that the latest image and the most recent version image are the same, run the following and compare the image IDs::

    docker inspect --format='{{.Id}}' docker-registry.pdmz.lasp.colorado.edu/ialirt/ialirt-<primary or secondary>:X.Y
    docker inspect --format='{{.Id}}' docker-registry.pdmz.lasp.colorado.edu/ialirt/ialirt-<primary or secondary>:latest

CDK Deployment
~~~~~~~~~~~~~
:ref:`cdk-deployment`

ECS Recognition of a New Image
~~~~~~~~~~~~~
To have ECS recognize a new image the cdk must be redeployed::

    aws ecs update-service --cluster <cluster name> --service <service name> --force-new-deployment --deployment-configuration maximumPercent=200,minimumHealthyPercent=0

