# python-recipie-book

## Getting started

In order to run this application you will need a mongodb instance to connect to, you can create one for free with mongodb [atlas](https://www.mongodb.com/resources/products/fundamentals/create-database) or create one in a docker container or however you like.

Once you have that you will need to supply the MONGO_URI to the app, the easiest way is to create a new file called `.env` in the root of this repo and add the following value to it:

```bash
MONGO_URI="mongodb://username:password@example.com:27017"
```

> **Note** You will need to update the username, password, url and port to match whatever your mongo uri is. You should be able to ask whoever setup your mongodb instance for it or get it from the atlas web page if you used that.

## Containerised version

There is now a containerised version of this app available on [dockerhub](https://hub.docker.com/repository/docker/grimvoodoo/cookbook/general) Which can be deployed either locally with docker or podman, or into kubernetes. You will still need a mongodb to connect to, but if you were to run this in kubernetes you could run a mongodb container in a sidecar.

## Using the recipe book

When you first start it you will see an empty page, becuase there are no recipies yet. First step is to create one, to do that click on the `Add New Recipe` button. That will take you to the page where you fill in the details of the recipe.

under ingredients you can clikc the `Add Ingredient` button to add as many rows as you like, I have set it up so you can just use the tab key to jump between the rows, it wont select the `-` button by using the tab button as I realised that accidentally deleting an entry was a likly scenario.

Once all the fields have been filled it then hit the `Add recipe` button. That will save the recipie into your Mongodb instance and take you back to the home page. You should now see your recipie in the chart, you can click on that to view the recipie.

## Further development

### Authentication

Currently there is no authentication and I would like to add that so the recipe book can be shared around or used in a public setting without strangers mess with your recipies.

### Experimentation

I created this partially becuase I wanted a way to track recipies other than just using bookmarks and partially because I wanted to see if I could make a web based recipie book. I have some improvements I want to add, like a working search function and maybe the ability to search by ingredients.

I have a vague idea of incorporating this into some kind of smart kitchen where you have ingredients kept on scales so the recipie list can auto-filter down what foods you can make based on the ingredients you have available but who knows if I will ever do anything with that.

I would like to try setting up a helm chart which can be used to deploy both the cookbook and its own database together to allow people quick and easy setups
