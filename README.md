# autotask4todoist
Automatically create new tasks when you complete tasks!

Depends on my other project [todoist2mqtt](https://github.com/toelke/todoist2mqtt).

The heavy lifting of reading the activitiy log is done by `todoist2mqtt`, `autotask4todoist` subscribes to updates on the MQTT-bus and creates tasks as needed.

To run:

```
docker run -d --restart=unless-stopped --name autotask4todoist -e TODOIST_API_KEY=123456789 toelke158/autotask4todoist:latest
```

Get the todoist API key from https://todoist.com/prefs/integrations (at the very bottom).

## Usage

On any task create a comment like this:

```
On Complete: Next Task 1 tomorrow @garden
```

When you close this task, `autotask4todoist` will automatically create a task just like if you typed in everything behind the `:` into the quick-add bar (in the example the task will be scheduled for tomorrow and have the label "garden").

You can also create multiple tasks by having multiple comments or by adding lines too the comment:

```
On Complete: Next Task 1 tomorrow @garden
On Complete: Next Task 2 in three days @home
```

You can also add a command for `autotask4todoist` to the newly-created task by adding them indented:

```
On Complete: Next Task 1 tomorrow @garden
  On Complete: Next Task 1a today @garden
  On Complete: Next Task 1b in 1 hour @home
On Complete: Next Task 2
```

This will create the two tasks "Next Task 1" and "Next Task 2" when you close the original task; when you complete the task "Next Task 1" `autotask4todoist` will create two new tasks "Next Task 1a" and "Next Task 1b" for you.

## Customization

Apart from using the environment variable `TODOIST_API_KEY` to set your API key, you can use the following environment variables:

* `MQTT_BROKER` to set the MQTT broker (default is 127.0.0.1)
* `MQTT_TOPIC` to set the MQTT topic (default is "todoist/activity")

# Disclaimer

This application is not created by, affiliated with, or supported by Doist.
