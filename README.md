<h1>Task summary</h1>
<p>The app represents a data management program that reads JSON data from a file and represents it in Excel format in 3 data layers.</p>

<p>
<b>How to compile:</b> python3 data_manager.py<br>
<b>Packages to install:</b> pandas, openpyxl, dotenv<br>
<b>Input:</b> the input file path can be set in ".env" configuration file. By default: "input.json" file in the current directory.
The input file is expected to contain rows representing JSON objects.<br>
<b>Output:</b> the path can be set in the ".env" configuration file. By default: "output.xlsx".
</p>

<h2>Layer 1</h2>
This part represents "Raw" sub-layer of "Staging" data layer. The data is stored "as-is", without flattening.
<ol>
  <li>Pandas DataFrame "df" representing data is created</li>
  <li>The DataFrame is exported to Excel ("layer1" sheet)</li>
</ol>
<i>Note:</br></i>
	In the current implementation the output data is replaced with each new start of a program.	

<h2>Layer 2</h2>
Data standardization starts. Now the data is cleansed: duplicate rows are deleted.</br>
Two rows are considered duplicate if the values of subset ["@timestamp", "agent", "application"] are equal.
<ol>
  <li>As there are nested objects in data, and we need to remove duplicated rows using data from fields inside the nested objects, the data first needs to be flattened (df_normalized – the DataFrame after flattening)</li>
  <li>In the raw data some of the agent.name fields include lowercase "x" and some – uppercase "X". I decided that subsets that differ only by case in this field should be considered equal, and because of that transformed values to one (upper) case before removing duplicates</li>
  <li>Then duplicates are removed and the result is written to the file ("layer2" sheet)</li>
</ol>

<i>Additional considerations:</i>
<ol type="a">
  <li>I decided to keep all the data, even if one of the key fields (for example, "@timestamp") is Null. It’s done to prevent data loss. Other possible strategies: drop the data row if any of the "key" column data is missing; inputing: replace the missing data when possible (for example, the application name can be deduced from the log file pathname)</li>
  <li>I suppose that "application" and "@timestamp" data elements are created automatically, so the format is already correct. If needed, on this step the format of the data can be checked (for example, that the string representing the timestamp is really a timestamp and, for example, that this timestamp is before the current point in time). It can be done with Pandas conversion functions (‘to_datetime’, ...)</li>
  <li>Also during this step, the names of the columns can be changed to more verbose ones that will be more understandable to a data consumer. But in order to do it, more information about the problem being solved is needed.</li>
  <li>I’ve decided to keep all data columns. Depending on the needs of data consumers, some of the columns with low-level information can be removed.</li>
</ol>

<h2>Layer 3</h2>
<p>The "layer3" sheet contains a summary with aggregated data: total number of data rows, number of data rows after removal, and number of rows with specific "process.Severity" and "application".</p>
<p>The data is divided: grouped by logging level ("processed.Severity").</br>
In the example data there are entries only of "INFO" and "WARN" logging levels, but data of any other level will also be processed.</p>
<ol>
  <li>The flattened data is grouped by "processed.Severity"</li>
  <li>The program iterates through groups</li>
  <li>Group data is sorted – primary by timestamp, secondary – by application</li>
  <li>The group data is exported to a separate labeled Excel sheet</li>
</ol>

<i>Considerations:</i>
<ol type="a">
  <li>I decided to separate data of different logging levels into separate labeled Excel sheets, to allow easier analysis. Depending on the logging level, this data will probably be analyzed by different people (or by the same people in different points in time).</li>
  <li>I sorted the data in each table, from most recent to least recent, in alphabetical order for the same timestamp. It can be done in different logic depending on the requirements.</li>
</ol>

<i>Additional considerations:</i>
<ol type="a">
  <li>Some of the "processed.message" data elements contain log data that can be parsed in the future. </li>
</ol>
