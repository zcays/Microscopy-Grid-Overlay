#.log Package
class LogFile:
    def __init__(self):
        self.device_name = None
        self.device_number = None
        self.software_version = None
        self.software_time_date = None
        self.run_id = None
        self.probe_device = None
        self.target = None
        self.pattern_layout_file = None
        self.humidity = None
        self.run_name = None

        self.task_names = []
        self.task_runs = {}
        self._current_task_run_id = 0

        self.nozzle = None
        self.x_fields = None
        self.y_fields = None
        self.start_point_left = None
        self.start_point_up = None
        self.x_field_gap = None
        self.y_field_gap = None
        self.pattern_size_x = None
        self.pattern_size_y = None
        self.dot_pitch_x = None
        self.dot_pitch_y = None
        self.field_points = {}

        self.parallel_spotting = None
        self.ignore_nozzle_offset = None
        self.sort_by_field_position = None

        self.repeat_found = False
        self.repeat_parameter_1 = None
        self.repeat_parameter_2 = None

        self.start_time = None
        self.finish_time = None
        self.recorded_humidity = []
        self.recorded_temperature = []
        self.extra_attributes = {}

    @classmethod
    def from_file(cls, filename):
        if not filename.lower().endswith(".log"):
            raise ValueError("File must be a .log file")

        result = cls()

        with open(filename, "r", encoding="utf-8", errors="replace") as file:
            lines = file.readlines()

        if not lines:
            return result

        result._read_device_line(lines[0])

        if len(lines) > 1:
            result._read_software_line(lines[1])

        current_field = None
        in_tasks = False
        in_field_points = False
        field_section = None
        in_event_log = False

        for line_number, original_line in enumerate(lines[2:], start=3):
            line = original_line.strip()

            if line.startswith("§"):
                continue

            if not line:
                if in_field_points and current_field is not None:
                    result.field_points[current_field].append(original_line.rstrip("\n"))
                elif in_tasks:
                    result.task_runs[result._current_task_run_id].append(original_line.rstrip("\n"))
                elif in_event_log:
                    result.task_runs[result._current_task_run_id].append(original_line.rstrip("\n"))
                continue

            if line.startswith("Run ID:"):
                result.run_id = result._after_colon(line)

            elif line.startswith("Probe:"):
                result.probe_device = result._after_colon(line)

            elif line.startswith("Target:"):
                result.target = result._after_colon(line)

            elif line.startswith("Pattern File"):
                result.pattern_layout_file = result._after_colon(line)

            elif line.startswith("Humidity:"):
                result.humidity = result._after_colon(line)

            elif line.startswith("Run Name:"):
                result.run_name = result._after_colon(line)

            elif line.startswith("Task Names:"):
                task_text = result._after_colon(line)

                result.task_names = [
                    name.strip()
                    for name in task_text.split("/")
                    if name.strip()
                ]

            elif line == "Tasks:":
                in_tasks = True
                result._current_task_run_id += 1
                result.task_runs[result._current_task_run_id] = []

            elif line.startswith("Nozzle(s):"):
                in_tasks = False
                result.nozzle = result._to_number(
                    result._after_colon(line)
                )

            elif in_tasks:
                result.task_runs[result._current_task_run_id].append(original_line.rstrip("\n"))

            elif line == "Field(s):":
                field_section = "fields"

            elif line == "Start Point":
                field_section = "start_point"

            elif line == "Pattern Size:":
                field_section = "pattern_size"

            elif line == "Dot Pitch:":
                field_section = "dot_pitch"

            elif line.startswith("Left:"):
                result.start_point_left = result._to_number(
                    result._after_colon(line)
                )

            elif line.startswith("Up:"):
                result.start_point_up = result._to_number(
                    result._after_colon(line)
                )

            elif line.startswith("X Field Gap:"):
                value = result._after_colon(line).rstrip("/")
                result.x_field_gap = result._to_number(value)

            elif line.startswith("Y Field Gap:"):
                value = result._after_colon(line).rstrip("/")
                result.y_field_gap = result._to_number(value)

            elif line.startswith("X ="):
                value = result._to_number(
                    line.split("=", 1)[1].strip()
                )

                if field_section == "fields":
                    result.x_fields = value
                elif field_section == "pattern_size":
                    result.pattern_size_x = value
                elif field_section == "dot_pitch":
                    result.dot_pitch_x = value

            elif line.startswith("Y ="):
                value = result._to_number(
                    line.split("=", 1)[1].strip()
                )

                if field_section == "fields":
                    result.y_fields = value
                elif field_section == "pattern_size":
                    result.pattern_size_y = value
                elif field_section == "dot_pitch":
                    result.dot_pitch_y = value

            elif line.startswith("Field ") and line[6:].isdigit():
                current_field = int(line[6:])
                result.field_points[current_field] = []
                in_field_points = True
                field_section = None

            elif line == "[0, 0, 0]":
                # Trigger line: start storing subsequent lines into list
                continue

            elif line.startswith("Drops/Field"):
                in_field_points = False
                current_field = None

            elif in_field_points and current_field is not None:
                result.field_points[current_field].append(original_line.rstrip("\n"))

            elif line.startswith("Parallel Spotting:"):
                result.parallel_spotting = result._on_or_off(
                    result._after_colon(line)
                )

            elif line.startswith("Ignore Nozzle Offset:"):
                result.ignore_nozzle_offset = result._on_or_off(
                    result._after_colon(line)
                )

            elif line.startswith("Sort by Field Position:"):
                result.sort_by_field_position = result._on_or_off(
                    result._after_colon(line)
                )

            elif line.startswith("Start Time:"):
                result.start_time = result._after_colon(line)
                in_event_log = True
                result._current_task_run_id += 1
                result.task_runs[result._current_task_run_id] = []
                continue

            elif line.startswith("Run has finished:"):
                result.finish_time = result._after_colon(line)
                in_event_log = False
                continue

            elif line.startswith("Run has been aborted!"):
                in_event_log = False
                continue

            elif in_event_log:
                if not line.startswith("Plate\tPlate Pos"):
                    result.task_runs[result._current_task_run_id].append(original_line.rstrip("\n"))
                if "Humidity=" in line:
                    result._read_recorded_environment(line)
                continue

            elif "Humidity=" in line:
                result._read_recorded_environment(line)

            elif ":" in line:
                label, value = line.split(":", 1)
                result._store_extra(label.strip(), value.strip())

        return result

    def _read_device_line(self, line):
        columns = [
            column.strip()
            for column in line.split("\t")
        ]

        if columns:
            self.device_name = columns[0] or None

        if len(columns) > 1:
            self.device_number = columns[1] or None

    def _read_software_line(self, line):
        columns = [
            column.strip()
            for column in line.split("\t")
        ]

        if columns:
            first_column = columns[0]

            if first_column.startswith("Software Version:"):
                self.software_version = self._after_colon(
                    first_column
                )

        if len(columns) > 1:
            self.software_time_date = columns[1] or None

    def _read_recorded_environment(self, line):
        humidity_text = line.split("Humidity=", 1)[1]
        humidity_part = humidity_text.split("Temperature=", 1)[0]
        humidity_value = humidity_part.strip().split()[0]

        self.recorded_humidity.append(
            self._to_number(humidity_value)
        )

        if "Temperature=" in line:
            temperature_text = line.split(
                "Temperature=", 1
            )[1].strip()

            temperature_value = temperature_text.split()[0]

            self.recorded_temperature.append(
                self._to_number(temperature_value)
            )

    def _store_extra(self, label, value):
        converted_value = self._to_number(value)

        if label not in self.extra_attributes:
            self.extra_attributes[label] = converted_value
        else:
            existing_value = self.extra_attributes[label]

            if not isinstance(existing_value, list):
                existing_value = [existing_value]
                self.extra_attributes[label] = existing_value

            existing_value.append(converted_value)

    @staticmethod
    def _after_colon(line):
        return line.split(":", 1)[1].strip()

    @staticmethod
    def _to_number(value):
        value = value.strip()

        try:
            return int(value)
        except ValueError:
            pass

        try:
            return float(value)
        except ValueError:
            return value

    @staticmethod
    def _on_or_off(value):
        value = value.strip().lower()

        if value == "on":
            return True

        if value == "off":
            return False

        return value

    def get_field_spots(self, field_id=1):
        """Returns a list of dicts [{'Row': r, 'Col': c, 'Value': val}] for all filled boxes in a field."""
        if field_id not in self.field_points:
            return []
        
        spots = []
        for r_idx, row in enumerate(self.field_points[field_id]):
            if isinstance(row, list):
                cells = row
            else:
                cells = row.split("\t")

            for c_idx, val in enumerate(cells):
                clean_val = val.strip()
                if clean_val != "" and clean_val != "[0, 0, 0]":
                    spots.append({"Row": r_idx, "Col": c_idx, "Value": clean_val})
        return spots

    def to_dataframe(self, field_id=1, format="matrix"):
        """
        Converts the specified field into a pandas DataFrame.
        format='matrix': 2D grid layout with active Row and Column headers.
        format='table': Database-style table with columns ['Row', 'Col', 'Value'].
        """
        spots = self.get_field_spots(field_id)
        if not spots:
            return None

        import pandas as pd
        df_spots = pd.DataFrame(spots)
        
        if format == "table":
            return df_spots
        else: # "matrix"
            pivot = df_spots.pivot(index="Row", columns="Col", values="Value").fillna("")
            return pivot

    def print_attributes(self):
        attribute_names = [
            "device_name",
            "device_number",
            "software_version",
            "software_time_date",
            "run_id",
            "probe_device",
            "target",
            "pattern_layout_file",
            "humidity",
            "run_name",
            "task_names",
            "nozzle",
            "x_fields",
            "y_fields",
            "start_point_left",
            "start_point_up",
            "x_field_gap",
            "y_field_gap",
            "pattern_size_x",
            "pattern_size_y",
            "dot_pitch_x",
            "dot_pitch_y",
            "field_points",
            "parallel_spotting",
            "ignore_nozzle_offset",
            "sort_by_field_position",
            "repeat_found",
            "repeat_parameter_1",
            "repeat_parameter_2",
            "start_time",
            "finish_time",
            "recorded_humidity",
            "recorded_temperature",
        ]

        for attribute_name in attribute_names:
            value = getattr(self, attribute_name)

            if value is not None and value != [] and value != {}:
                if attribute_name == "field_points":
                    for field_id in value:
                        print("field_points, Field " + str(field_id) + ":")
                        spots = self.get_field_spots(field_id)
                        if spots:
                            try:
                                df_matrix = self.to_dataframe(field_id, format="matrix")
                                print(df_matrix.to_string())
                            except Exception:
                                print(f"{'Row':<6} {'Col':<6} {'Value':<10}")
                                print("-" * 25)
                                for s in spots:
                                    print(f"{s['Row']:<6} {s['Col']:<6} {s['Value']:<10}")
                        
                        if len(value) > 1:
                            print("... (additional fields omitted from print)")
                        break
                else:
                    print(attribute_name + " = " + str(value))

        for attribute_name, value in self.extra_attributes.items():
            print(attribute_name + " = " + str(value))

        for run_id, lines in self.task_runs.items():
            print("\nTask Ran " + str(run_id) + ":")
            for line in lines:
                print(line)


# ---------------------------------------------------------
# TEST THE LOG FILE
# ---------------------------------------------------------

filename = "/Users/ivanchao/Library/CloudStorage/GoogleDrive-chaoivan27@gmail.com/.shortcut-targets-by-id/1Xn6WT8ajf-erXPdHQRJBtF93D5sWzidM/ext-Internship2026/data/print/print103/print103_lyt0run1_20240919_1_133043/print103_lyt0run1_20240919_1_133043_Logfile.log"

try:
    log_data = LogFile.from_file(filename)

    print("\\n--- LOG FILE RESULTS ---")
    log_data.print_attributes()

except ValueError as error:
    print("Invalid file: " + str(error))

except FileNotFoundError:
    print("File not found: " + filename)

except PermissionError:
    print("Permission denied: " + filename)

except OSError as error:
    print("Could not read file: " + str(error))
