"""GMK a.k.a Game Master Kit.\nThis module/kit generates anything that will remain constant throughout the game (essentially).\nThere tools are not meant for a normal player, for they have the ability of cheating, in a way."""
if __name__ == 'GMK':
	from GMK import items
	from GMK import world_builder
else:
	import items
	import world_builder