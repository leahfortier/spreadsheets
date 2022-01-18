class Date implements Comparable<Date>
{
	int month, day, year;
	Date(int month, int day, int year)
	{
		this.month = month;
		this.day = day;
		
		// Handle two-digit years
		if((year+"").length() == 2)
		{
			year += 2000;
		}
		this.year = year;
	}
	
	/*
	 * Create Date object from date in mm/dd/yy or mm/dd/yyyy format
	 */
	static Date fromMDYSlash(String s)
	{
		String[] tokens = s.split("/");
		int month = Integer.parseInt(tokens[0]);
		int day = Integer.parseInt(tokens[1]);
		int year = Integer.parseInt(tokens[2]);
		return new Date(month, day, year);
	}
	
	/*
	 * Create Date object from date in yyyy-mm-dd format
	 */
	static Date fromYMDDash(String s)
	{
		String[] tokens = s.split("-");
		int year = Integer.parseInt(tokens[0]);
		int month = Integer.parseInt(tokens[1]);
		int day = Integer.parseInt(tokens[2]);
		return new Date(month, day, year);
	}
	
	@Override
	public int compareTo(Date o)
	{
		if(year != o.year)
		{
			return year - o.year;
		}
		if(month != o.month)
		{
			return month - o.month;
		}
		return day - o.day;
	}
	
	/*
	 * When printing the date use the format mm/dd/yyy
	 */
	public String toString()
	{
		return String.format("%02d/%02d/%d", month, day, year);
	}
}