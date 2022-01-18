import java.io.File;
import java.io.FileInputStream;
import java.io.PrintWriter;
import java.time.LocalDate;
import java.time.ZoneId;
import java.util.Scanner;
import java.util.TreeMap;

public class ReformatProgress
{
	static String PROGRESS_FILE = "../main/progress.csv";
	static String UPDATED_PROGRESS_FILE = "../main/reformattedprogress.csv";
	public static void main(String[] args) throws Exception
	{
		//Read the original progress table
		Scanner input = new Scanner(new FileInputStream(new File(PROGRESS_FILE)));
		Table progressTable = new Table(input.nextLine(), ',');
		while(input.hasNext())
		{
			String line = input.nextLine();
			if(line.length() == 0)
			{
				continue;
			}
			if(progressTable.addRow(line) != 0)
			{
				throw new Exception("Incorrectly formatted row:\n  " + line);
			}
		}
		input.close();
		
		// Get today's date and store in a Date object
		LocalDate todayPST = LocalDate.now(ZoneId.of("America/Los_Angeles"));
		Date today = Date.fromYMDDash(todayPST.toString());
		
		//Get best time for each unique stage and append row with today's date for each
		TreeMap<UniqueStage, Time> bestTimes = getBestTimes(progressTable);
		for(UniqueStage stage : bestTimes.keySet())
		{
			int val = progressTable.addRow(today, stage, "Speed", bestTimes.get(stage).toString());
			System.out.println(val);
		}
		System.out.println("Number of rows: " + progressTable.data.size());
		
		// Reformat times to add hours field for consistency in plotting
		for(int i = 0; i<progressTable.data.size(); i++)
		{
			if(!progressTable.query(i, "Type").equals("Speed"))
			{
				continue;
			}
			String value = progressTable.query(i, "Value");
			if(value.equals("--"))
			{
				continue;
			}
			progressTable.set(i, "Value", Time.fromString(value).toString());
		}
		
		// Output updated table
		PrintWriter out = new PrintWriter(new File(UPDATED_PROGRESS_FILE));
		out.println(progressTable);
		out.close();
	}
	
	/*
	 * Get the best time ever for each (Player, Mode, Chapter) triplet
	 */
	static TreeMap<UniqueStage, Time> getBestTimes(Table dataTable)
	{
		TreeMap<UniqueStage, Time> bestTimes = new TreeMap<UniqueStage, Time>();
		for(int i = 0; i<dataTable.data.size(); i++)
		{
			if(!dataTable.query(i, "Type").equals("Speed"))
			{
				continue;
			}
			UniqueStage curStage = UniqueStage.fromTableRow(dataTable, i);
			String value = dataTable.query(i, "Value");
			if(value.equals("--"))
			{
				continue;
			}
			Time t = Time.fromString(value);
			if(!bestTimes.containsKey(curStage) || bestTimes.get(curStage).compareTo(t) > 0)
			{
				bestTimes.put(curStage, t);
			}
		}
		return bestTimes;
	}
}
