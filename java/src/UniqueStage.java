/*
 * A (player, mode, chapter) triplet representing a unique stage
 */
public class UniqueStage implements Comparable<UniqueStage>
{
	String player, mode, chapter;
	UniqueStage(String player, String mode, String chapter)
	{
		this.player = player;
		this.mode = mode;
		this.chapter = chapter;
	}
	
	static UniqueStage fromTableRow(Table data, int index)
	{
		String player = data.query(index, "Player");
		String mode = data.query(index, "Mode");
		String chapter = data.query(index, "Chapter");
		return new UniqueStage(player, mode, chapter);
	}

	@Override
	public int compareTo(UniqueStage o)
	{
		if(!player.equals(o.player))
		{
			return player.compareTo(o.player);
		}
		if(!mode.equals(o.mode))
		{
			return mode.compareTo(o.mode);
		}
		return chapter.compareTo(o.chapter);
	}
}
