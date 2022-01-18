public class Time implements Comparable<Time>
{
	int hours;
	int minutes;
	double seconds;
	
	int totalMs;
	
	static int MS_PER_HOUR = 60 * 60 * 1000;
	static int MS_PER_MINUTE = 60 * 1000;
	
	Time(int hours, int minutes, double seconds)
	{
		this.hours = hours;
		this.minutes = minutes;
		this.seconds = seconds;
		totalMs = (int)(seconds*1000 + .5) +
				minutes * MS_PER_MINUTE +
				hours * MS_PER_HOUR;
	}
	
	Time(int totalMs)
	{
		this.totalMs = totalMs;
		hours = totalMs / MS_PER_HOUR;
		totalMs %= MS_PER_HOUR;
		minutes = totalMs / MS_PER_MINUTE;
		totalMs %= MS_PER_MINUTE;
		seconds = totalMs / 1000.0;
	}
	
	/*
	 * Parse times in m:ss.sss or h:mm:ss.sss
	 */
	static Time fromString(String s)
	{
		String[] tokens = s.split(":");
		double seconds = Double.parseDouble(tokens[tokens.length - 1].replaceAll(" ", "."));
		int minutes = Integer.parseInt(tokens[tokens.length - 2]);
		int hours = tokens.length > 2 ? Integer.parseInt(tokens[tokens.length - 3]) : 0;
		return new Time(hours, minutes, seconds);
	}
	
	/*
	 * Output times as m:ss.sss or h:mm:ss.sss
	 */
	public String toString()
	{
		return String.format("%d:%02d:%06.3f", hours, minutes, seconds);
	}

	@Override
	public int compareTo(Time o)
	{
		return totalMs - o.totalMs;
	}
}
