import { Alert, Button, Snackbar } from "@material-ui/core";
import { useState } from "react";

export default function DeleteAlarm() {
  const URL = "http://raspberrypi.local";
  const [open, setOpen] = useState(false);

  const removeAlarm = async () => {
    setOpen(false);
    const response = await fetch(`${URL}/clear`, {
      method: "GET",
      mode: "no-cors",
      headers: {
        "Content-Type": "application/json",
      },
    });
    console.log(response);
    setOpen(true);
  };

  const handleClose = (event, reason) => {
    setOpen(false);
  };

  return (
    <>
      <Button color="secondary" onClick={() => removeAlarm()}>
        Remove current alarm
      </Button>
      <Snackbar open={open} autoHideDuration={6000} onClose={handleClose}>
        <Alert onClose={handleClose} severity="success">
          Alarm has been removed successfully!
        </Alert>
      </Snackbar>
    </>
  );
}
