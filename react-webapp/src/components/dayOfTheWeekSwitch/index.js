import Switch from "@material-ui/core/Switch";
import { Container } from "./style";

function DayOfTheWeekSwitch({ checked, handleChange, name, label }) {
  return (
    <Container>
      {label}
      <Switch
        checked={checked}
        onChange={handleChange}
        color="primary"
        name={name}
        inputProps={{ "aria-label": "primary checkbox" }}
      />
    </Container>
  );
}

export default DayOfTheWeekSwitch;
