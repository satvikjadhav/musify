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

#### Usage

To build the executable, run

    $ sbt assembly
    $ # make sure the script is executable
    $ chmod +x bin/eventsim

(By the way, eventsim requires Java 8.)

The program can accept a number of command line options:

    $ bin/eventsim --help
          -a, --attrition-rate  <arg>    annual user attrition rate (as a fraction of
                                         current, so 1% => 0.01) (default = 0.0)
          -c, --config  <arg>            config file
              --continuous               continuous output
              --nocontinuous             run all at once
          -e, --end-time  <arg>          end time for data
                                         (default = 2016-01-06T15:02:33.785)
          -f, --from  <arg>              from x days ago (default = 15)
              --generate-counts          generate listen counts file then stop
              --nogenerate-counts        run normally
              --generate-similars        generate similar song file then stop
              --nogenerate-similars      run normally
          -g, --growth-rate  <arg>       annual user growth rate (as a fraction of
                                         current, so 1% => 0.01) (default = 0.0)
          -k, --kafkaBrokerList  <arg>   kafka broker list
          -n, --nusers  <arg>            initial number of users (default = 1)
          -r, --randomseed  <arg>        random seed
          -s, --start-time  <arg>        start time for data
                                         (default = 2015-12-30T15:02:33.839)
              --tag  <arg>               tag applied to each line (for example, A/B test
                                         group)
          -t, --to  <arg>                to y days ago (default = 1)
              --useAvro                  output data as Avro
              --nouseAvro                output data as JSON
          -u, --userid  <arg>            first user id (default = 1)
          -v, --verbose                  verbose output (not implemented yet)
              --noverbose                silent mode
              --help                     Show help message

         trailing arguments:
          output-dir (not required)   Directory for output files

Only the config file is required.

Parameters can be specified in three ways: you can accept the default value, you can specify them in the config file,
or you can specify them on the command line. Config file values override defaults; command line options override
everything.

Example for about 2.5 M events (1000 users for a year, growing at 1% annually):

    $ bin/eventsim -c "examples/site.json" --from 365 --nusers 1000 --growth-rate 0.01 data/fake.json
    Initial number of users: 1000, Final number of users: 1010
    Starting to generate events.
    Damping=0.0625, Weekend-Damping=0.5
    Start: 2013-10-06T06:27:10, End: 2014-10-05T06:27:10, Now: 2014-10-05T06:27:07, Events:2468822

Example for more events (30,000 users for a year, growing at 30% annually):

    $ bin/eventsim -c "examples/site.json" --from 365 --nusers 30000 --growth-rate 0.30 data/fake.json
