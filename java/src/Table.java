import java.util.ArrayList;
import java.util.HashMap;

/*
 * A data table parsed from a tsv or csv file
 */
class Table
{
	// fieldNames is an array of column names
	String[] fieldNames; 

	// fieldToIndex maps column names to column index
	HashMap<String, Integer> fieldToIndex;
	
	// data is a list of rows in the table
	ArrayList<String[]> data;
	
	// delim is the character separating columns within each row
	char delim;
	
	Table(String header, char delim)
	{
		this.delim = delim;
		String[] tokens = header.split(delim+"");
		fieldNames = new String[tokens.length];
		fieldToIndex = new HashMap<String, Integer>();
		for(int i = 0; i<tokens.length; i++)
		{
			fieldNames[i] = tokens[i].trim();
			fieldToIndex.put(fieldNames[i], i);
		}
		data = new ArrayList<String[]>();
	}
	
	/*
	 * Adds a row given a date, stage identifier, and type/value.
	 * Assumes columns are {Date, Player, Mode, Chapter, Type, Value} in some order
	 * If this is true then the new row will be added and 0 wll be returned.
	 * If not, the table will be unchanged and the method will return -1.
	 */
	int addRow(Date date, UniqueStage stage, String type, String value)
	{
		String[] expectedRows = new String[] {"Date", "Player", "Mode",
				"Chapter", "Type", "Value"
		};
		if(fieldNames.length != expectedRows.length)
		{
			return -1;
		}
		for(String s : expectedRows)
		{
			if(!fieldToIndex.containsKey(s))
			{
				return -1;
			}
		}
		String[] newRow = new String[expectedRows.length];
		newRow[fieldToIndex.get("Date")] = date.toString();
		newRow[fieldToIndex.get("Player")] = stage.player;
		newRow[fieldToIndex.get("Mode")] = stage.mode;
		newRow[fieldToIndex.get("Chapter")] = stage.chapter;
		newRow[fieldToIndex.get("Type")] = type;
		newRow[fieldToIndex.get("Value")] = value;
		data.add(newRow);
		return 0;
	}
	
	/*
	 * Adds a row to the table - the delimiter is assumed to match the header
	 * Return 0 if success, or -1 otherwise
	 */
	int addRow(String line)
	{
		String[] tokens = line.split(delim+"");
		
		String[] newRow = new String[tokens.length];
		for(int i = 0; i<tokens.length; i++)
		{
			newRow[i] = tokens[i].trim(); // Spaces are trimmed from each field
		}
		
		if(newRow.length != fieldNames.length)
		{
			return -1; 
		}
		
		data.add(newRow);
		return 0;
	}
	
	/*
	 * Return the value on a given row for a particular field
	 * If the field doesn't exist or row index too large, "" will be returned.
	 */
	String query(int row, String field)
	{
		if(!fieldToIndex.containsKey(field) || row >= data.size())
		{
			return "";
		}
		return data.get(row)[fieldToIndex.get(field)];
	}
	
	/*
	 * Sets a value of a particular field in a given row
	 */
	void set(int row, String field, String value)
	{
		if(!fieldToIndex.containsKey(field) || row >= data.size())
		{
			return;
		}
		data.get(row)[fieldToIndex.get(field)] = value;
	}
	
	public String toString()
	{
		StringBuilder sb = new StringBuilder("");
		for(int i = 0; i<fieldNames.length; i++)
		{
			sb.append(fieldNames[i]);
			sb.append(i == (fieldNames.length-1) ? "\n" : delim);
		}
		for(String[] row : data)
		{
			for(int i = 0; i<row.length; i++)
			{
				sb.append(row[i]);
				sb.append(i == (row.length-1) ? "\n" : delim);
			}
		}
		return sb.toString();
	}
}