import { Alert, Button, Snackbar } from "@material-ui/core";

import TextField from "@material-ui/core/TextField";
import AdapterDateFns from "@material-ui/lab/AdapterDateFns";
import LocalizationProvider from "@material-ui/lab/LocalizationProvider";
import TimePicker from "@material-ui/lab/TimePicker";
import { useEffect, useState } from "react";
import DayOfTheWeekSwitch from "../dayOfTheWeekSwitch";
import DeleteAlarm from "../deleteAlarm";
import { Container, DaysOfTheWeekContainer } from "./style";

function NewAlarm() {
  const [open, setOpen] = useState(false);
  const [time, setTime] = useState(new Date());
  const [daysOfTheWeek, setDaysOfTheWeek] = useState({
    Mo: false,
    Tu: false,
    We: false,
    Th: false,
    Fr: false,
    Sa: false,
    Su: false,
  });
  const URL = "http://raspberrypi.local";

  const handleChange = (event) => {
    setDaysOfTheWeek({
      ...daysOfTheWeek,
      [event.target.name]: event.target.checked,
    });
  };

  const addAlarm = async () => {
    setOpen(false);
    const alarm = {
      time: time.toLocaleTimeString(),
      daysOfTheWeek: daysOfTheWeek,
    };
    console.log(new Date().toISOString().slice(0, 19));
    console.log(alarm);

    const response = await fetch(`${URL}/set2?time=${alarm.time}`, {
      method: "POST",
      mode: "no-cors",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(alarm),
    });
    setOpen(true);
    console.log(response);
  };

  const handleClose = (event, reason) => {
    setOpen(false);
  };

  return (
    <Container>
      <h1>Set alarm</h1>

      <LocalizationProvider dateAdapter={AdapterDateFns}>
        <Container>
          <TimePicker
            ampm={false}
            openTo="hours"
            views={["hours", "minutes", "seconds"]}
            inputFormat="HH:mm:ss"
            mask="__:__:__"
            label="Select time"
            value={time}
            onChange={(newValue) => {
              setTime(newValue);
            }}
            renderInput={(params) => <TextField {...params} margin="normal" />}
          />
        </Container>
      </LocalizationProvider>

      <DaysOfTheWeekContainer>
        <DayOfTheWeekSwitch
          checked={daysOfTheWeek.Mo}
          handleChange={handleChange}
          name="Mo"
          label="Mon"
        />
        <DayOfTheWeekSwitch
          checked={daysOfTheWeek.Tu}
          handleChange={handleChange}
          name="Tu"
          label="Tue"
        />
        <DayOfTheWeekSwitch
          checked={daysOfTheWeek.We}
          handleChange={handleChange}
          name="We"
          label="Wed"
        />
        <DayOfTheWeekSwitch
          checked={daysOfTheWeek.Th}
          handleChange={handleChange}
          name="Th"
          label="Thu"
        />
        <DayOfTheWeekSwitch
          checked={daysOfTheWeek.Fr}
          handleChange={handleChange}
          name="Fr"
          label="Fri"
        />
        <DayOfTheWeekSwitch
          checked={daysOfTheWeek.Sa}
          handleChange={handleChange}
          name="Sa"
          label="Sat"
        />
        <DayOfTheWeekSwitch
          checked={daysOfTheWeek.Su}
          handleChange={handleChange}
          name="Su"
          label="Sun"
        />
      </DaysOfTheWeekContainer>
      <Button onClick={addAlarm}>Save alarm</Button>
      <div style={{ margin: "1em" }}></div>
      <DeleteAlarm />
      <Snackbar open={open} autoHideDuration={6000} onClose={handleClose}>
        <Alert onClose={handleClose} severity="success">
          Alarm has been set successfully!
        </Alert>
      </Snackbar>
    </Container>
  );
}

export default NewAlarm;
