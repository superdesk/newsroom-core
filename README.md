# Superdesk Newshub a.k.a. Newsroom

Newshub is a secure self-service content store, fed by outputs from a Superdesk content management system.

Each user has a password-protected Newshub account, which is accessible online from anywhere. 

Users may browse lists of articles filtered by source, topic, region - or by any classification/metadata system employed. Archived content is equally available.

Users may bookmark (save) items of interest for later download, or multiple-select items in a list for download in one, zipped file.

If a user is particularly interested in an article, they may choose to “follow” that topic, and be alerted by email to any updates or developments. 

Articles may be downloaded in NITF, NewsML G2, or as plain text. 

Users may also share items with their colleagues and comment on them.

Superdesk Newshub was developed in partnership with the Australian Associated Press news agency. Its Newshub instance, which it brands “AAP Newsroom”, is fed by the agency’s Superdesk production CMS. 

Newshub is fully responsive from desktop, to tablet, to mobile.

Sourcefabric is happy to provide demonstrations of Newshub and other newsroom tools from the Superdesk stable.

## Install && Run

See https://github.com/superdesk/newsroom-core

## Design App

A static react app is available for design purposes. It does not require a back-end to be running.

To install & start the design app, run the following:

```
npm install
npm run design-app
```

The design app shares the same style (```assets/styles```) and assets (```newsroom/static```) as the full Newshub application.


## Test Python app

There is syntax and code style checker:

```
flake8 newsroom 
```

And tests:

```
pytest
```

and

```
behave
```

## Test Javascript code

Check syntax via eslint:

```
npm run lint
```

Or test code using karma & jasmine:

```
npm run test
```

for single run, or to watch for changes:

```
npm run test start
```

## Translations

### Extract messages

```
$ python setup.py extract_messages
```

Will create `messages.pot` file in root folder. You can use it to update
strings on transifex or init a new language:

```
$ python setup.py init_catalog -l <locale>
```

### Translate

We translate on [transifex](https://www.transifex.com/sourcefabric/superdesk-newshub/).

### Adding translated po files

Download translated messages file from transifex and save it
in locale dir: `newsroom/translations/<locale>/LC_MESSAGES/messages.po`.

Then run compile to generate mo files for server messages:

```
$ python setup.py compile_catalog -l <locale>
```

When compiled you can add locale to `settings.LANGUAGES` to enable it.



test test
