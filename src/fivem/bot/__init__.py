import importlib
import logging
import os
import pkgutil
import typing as t


import asyncpg
import disnake
from disnake.ext import commands
from disnake.ext.commands import AutoShardedInteractionBot


intents = disnake.Intents(guilds=True, members=True)


def walk_modules(
    paths: t.Iterable[str],
    prefix: str = "",
    ignore: t.Iterable[str] = None
) -> t.Iterator[str]:

    if isinstance(ignore, t.Iterable):
        ignore_tup = tuple(ignore)
        def ignore(path): return path.startswith(ignore_tup)

    seen: set[str] = set()

    for _, name, ispkg in pkgutil.iter_modules(paths, prefix):
        if ignore is not None and ignore(name):
            continue

        if not ispkg:
            yield name
            continue

        module = importlib.import_module(name)

        if hasattr(module, "setup"):
            yield name
            continue

        sub_paths: list[str] = []

        for path in module.__path__ or ():
            if path not in seen:
                seen.add(path)
                sub_paths.append(path)

        if sub_paths:
            yield from walk_modules(sub_paths, name + ".", ignore)


class FiveMBot(AutoShardedInteractionBot):
    def __init__(self):
        self.embed_cooldown = commands.CooldownMapping.from_cooldown(
            1, 120, commands.BucketType.user)

        super().__init__(owner_id=485183782328991745, intents=intents)

    async def create_db_pool(self):
        self.db = await asyncpg.create_pool(
            dsn="postgres://vanity2:monster95@174.53.67.214:5432/fivem")
        logging.info("db connected")

    def _load_extensions(
        self,
        root_module: str,
        *,
        package: str = None,
        ignore: t.Iterable[str] = None,
    ) -> None:
        if "/" in root_module or "\\" in root_module:
            path = os.path.relpath(root_module)
            if ".." in path:
                raise ValueError(
                    "Paths outside the cwd are not supported. Try using the module name instead."
                )
            root_module = path.replace(os.sep, ".")

        root_module = self._resolve_name(root_module, package)

        if (spec := importlib.util.find_spec(root_module)) is None:
            raise commands.ExtensionError(
                f"Unable to find root module '{root_module}'", name=root_module
            )

        if (paths := spec.submodule_search_locations) is None:
            raise commands.ExtensionError(
                f"Module '{root_module}' is not a package", name=root_module
            )
        for module_name in walk_modules(paths, f"{spec.name}.", ignore):
            self.load_extension(module_name)
            logging.info(f"loaded {module_name}")
