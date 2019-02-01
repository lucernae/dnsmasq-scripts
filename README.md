# Local DNS resolver via Docker

## What is this about

I'm sometimes a web developer, full stack engineer, or dev ops who deals with 
resolver a lot. Most of the time, when we develop web apps using Docker, 
we end up with a big mess of convoluted system trying to talk each other. 
Since most of the time my job would be to make sure it talks correctly,
I have to arrange so all these sandboxed service can talk with each other.

DNS resolver in local development environment is useful to assign meaningful 
name for your web service. It could be `frontend.test` or `backend.test` or
anything useful to avoid using ip address that could change (well because 
I work remotely most of the time and changes place often).

This repo here is just to help my work, and if you could find anything useful, 
you can use it. But keep in mind that these repo is shared without guarantee. 

You know what I mean ;).

By the way, currently this repo deals with the script in OSX. 
I had different script in Linux. I will put it here when I have time.

## How this is useful

Useful for mainly:

- You need meaningful dns name for local development like `frontend.test`
- Your ISP is sh*t and obscured/tamper with dns queries (it is in my case)

## How it works

Ok, let me explain how this works in big picture. I work in OSX, Linux, and 
sometimes Windows. So, I need an OS independent way of making sure my setup 
works in different OSes. So I used Docker. I assume you know Docker and have 
it installed. Otherwise it doesn't work.

I setup a dns resolver from `dnsmasq` a handy software to setup your own 
resolver. I used it via Docker. You could, of course install dnsmasq via 
homebrew or your linux distros package manager. But then this thing is not 
for you. I used via Docker image `jpillora/dnsmasq` also a nice guy. 
Look at the repo yourself if you're interested: https://github.com/jpillora/docker-dnsmasq

This docker image will serve as the main resolver, so you need to reserve port 53 
to this container (that makes it incompatible with your installed dnsmasq, 
if you have them already). Basically all incoming DNS queries will be handled 
by this container.

Then to make the OS knows that it had to query DNS through this container, 
the script set up OSX main dns resolver to the interface's ipaddress.
Why the interface's ip? At the time I wrote the script the container's ip 
is dynamic. So I had to *pin* it down so the port is exposed to the known
interface's ip address. Like the Wi-Fi card (or other interface if in the 
future docker will have it's own interface bridge accessible).

It then query the current ipaddress of the interface and tell OSX to use 
that one for DNS query. This makes sure anything you do through OSX went 
through dnsmasq first. If you query some domain from the browser, 
the query gets delivered to interface ipaddress, to dnsmasq container, 
to dnsmasq service, then forwarded to primary dns you setup in dnsmasq conf.

In addition to above scenario, the script also setup a local domain name of 
your choice, in my case, the `.test` first level domain. 
This means everytime I query domain that ends with `.test`, OSX will return 
the ipadress of the interface you choose to setup this script. It is best 
to use an ipaddress that is resolvable from inside docker container 
(again like the Wi-Fi card) and from your mac. This will cover use case 
when your docker service needs to refer to itself and pass it's domain name 
to other docker service. For example to construct the SITEURL or base url.

## How to use

### Prepare dnsmasq.conf

Copy over `dnsmasq.conf.sample` into `dnsmasq.conf` and configure it.
You are interested in the last two line:

```
server=8.8.8.8
address=/test/192.168.1.8
```

The server directives is the primary DNS of your choice (8.8.8.8 is Google's).
The address directive means `.test` domain will resolve to ip `192.168.1.8`.
It is ok to use this ip now, because it will be changed by the script anyway.

### Prepare docker_dnsmasq.sh

Copy over `docker_dnsmasq.sample.sh` into `docker_dnsmasq.sh` and configure it.
This is a docker run command to spin up dnsmasq container.
You are interested in the following settings:

```
-v /<your conf location>/dnsmasq.conf:/etc/dnsmasq.conf \
```

Change `/<your conf location>/dnsmasq.conf` to the actual location of your conf file.
Or, if it is in the same directory with this script, you can use `./dnsmasq.conf`

```
-p 5380:8080 \
```

5380 is the port of the web admin interface of dnsmasq (yes the author provided it. how nice.)
Change it to port that you like.

```
-e "HTTP_USER=foo" \
-e "HTTP_PASS=bar" \
```

Credentials for the previous web admin interface mentioned.

```
--name dnsmasq \
```

Container name. Choose something that is easy to remember.

### Prepare local_resolver.sh

Copy over `local_resolver.sample.sh` into `local_resolver.sh` and configure it.
This is the script that you actually execute to suit your profile. 

The script just contains command execution of `local_resolver.py` with arguments:

1. The interface name to bind to
2. The location of dnsmasq.conf, make it an absolute path so the script can 
   be executed from anywhere and the path resolves correctly.
3. The location of the resolver file to update. Make one if you don't have any now.
   Usually put it in `/etc/resolver/<domain name>`
4. The name of the domain to resolve for development. In this example `.test`
   top level domain.
   
### Create an alias to call the script from anywhere

If you changed work place often like me, you might want to create alias to execute 
`local_resolver.sh` from anywhere in your computer. Pick any method you usually do.

Using alias:

Create an alias in your .bashrc files (or equivalently other rc files if you use other shell)

```
alias dnsmasq_restart='/Users/lucernae/Scripts/local_resolver.sh'
```

Using soft links to /usr/local/bin:

execute from terminal:

```
ln -s /Users/lucernae/Scripts/local_resolver.sh /usr/local/bin/dnsmasq_restart
```

### Call the script

Just call your shortcut. In my case:

```
dnsmasq_restart
```
