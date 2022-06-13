## Eventsim

Eventsim is a program, written in Scala, that generates event data to replicate page requests for a fake music web site (picture something like Spotify); the results look like real use data, but are randomly generated. You can find the original repo [here](https://github.com/Interana/eventsim). This docker image is borrowed from [viirya's clone](https://github.com/viirya/eventsim) of it, as the original project has gone without maintenance for a few years now.

### Setup

#### Docker Image
```bash
docker build -t events:1.0 .
```

#### Run With Kafka Configured On Localhost
```bash
docker run -it \
  --network host \
  events:1.0 \
    -c "examples/example-config.json" \
    --start-time "`date +"%Y-%m-%dT%H:%M:%S"`" \
    --end-time "2022-03-18T17:00:00" --nusers 20000 \
    --kafkaBrokerList localhost:9092 \
    --continuous
```

### Config and Usage

#### Config

Take a look at the sample config file. It's a JSON file, with key-value pairs.  Here is an explanation of the values
(many of which match command line options):

* `seed` For the pseudo-random number generator. Changing this value will change the output (all other parameters
being equal).
* `alpha` This is the expected number of seconds between events for a user. This is randomly generated from a lognormal
distrbution
* `beta` This is the expected session interarrival time (in seconds). This is thirty minutes plus a randomly selected
value from an exponential distribution
* `damping` Controls the depth of daily cycles (larger values yield stronger cycles, smaller yield milder)
* `weekend-damping` Controls the difference between weekday and weekend traffic volume
* `weekend-damping-offset` Controls when the weekend/holiday starts (relative to midnight), in minutes
* `weeeknd-damping-scale` Controls how long traffic tapering lasts, in minutes
* `session-gap` Minimum time between sessions, in seconds
* `start-date` Start date for data (in ISO8601 format)
* `end-date` End date for data (in ISO8601 format)
* `n-users` Number of users at start-date
* `first-user-id` User id assigned to first user (these are assigned sequentially)
* `growth-rate` Annual growth rate for users
* `tag` Tag added to each line of the output

You also specify the event state machine. Each state includes a page, an HTTP status code, a user level, and an
authentication status. Status should be used to describe a user's status: unregistered, logged in, logged out,
cancelled, etc. Pages are used to describe a user's page. Here is how you specify the state machine:

* Transitions. Describe the pair of page and status before and after each transition, and the
probability of the transition.
* New user. Describes the page and status for each new user (and probability of arriving for the
first time with one of those states).
* New session. Describes that page and status for each new session.
* Show user details. For each status, states whether or not users are shown in the generated event log.

When you run the simulator, you specify the mean values for alpha and beta and the simulator picks values for specific
users.
