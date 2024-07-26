import csv
import json
import os

from typing import Any, Callable, Iterable
from io import TextIOWrapper


# hack: inherit from string to allow using this class instead of path represented as string
class Directory(str):
	def __new__(cls, dir_path: str=".") -> "Directory": # have to use "Directory" since cannot use the class itself inside its definition
		"""
		Directory constructor.
		Creates the directory if it does not exist.

		Parameters
		----------
		dir_path : str, default="."
			| path to the directory
		"""

		if not os.path.isdir(dir_path):
			os.makedirs(dir_path, exist_ok=True)
		return super().__new__(cls, dir_path)


	def listdir(self) -> list[str]:
		"""
		Gets a list of everything in the directory and returns it as a list of strings.

		Returns
		-------
		list[str]
			| list of files and subdirectories in the directory
		"""

		return os.listdir(self)


	def listfiles(self) -> list[str]:
		"""
		Gets a list of only the files in the directory and returns it as a list of strings.

		Returns
		-------
			| list of files in the directory
		"""

		return list(filter(os.path.isfile, self.listdir()))


	def clear(self, paths: list[str]) -> None:
		"""
		Deletes those entires in `paths` that exist.

		Parameters
		----------
		paths : list[str]
			| list of paths to items to be deleted
		"""

		path: str
		for path in paths:
			if os.path.exists(path):
				os.remove(path)


	def cleardir(self) -> None:
		"""
		Deletes everything in the directory.
		"""

		self.clear([os.path.join(self, path) for path in self.listdir()])


	def clearfiles(self) -> None:
		"""
		Deletes all the files in the directory.
		"""

		self.clear([os.path.join(self, path) for path in self.listfiles()])


class File:
	dir: Directory
	filename: str

	_path: str

	def __init__(self, dir: Directory, filename: str) -> None:
		"""
		File initialiser.

		Parameters
		----------
		dir : Directory
			| a Directory type representing where the file will be stored
		filename : str
			| name of the file
		"""

		self.dir = dir
		self.filename = filename

		self._path = os.path.join(dir, filename)


	def __str__(self) -> str:
		return f"<File path={self._path}>"


	def exists(self) -> bool:
		"""
		Checks if the file the instance is representing exists.

		Returns
		-------
		bool
			| `True` if it exists otherwise `False`
		"""

		return os.path.exists(self._path)

	
	def write(self, writer: Callable[[TextIOWrapper], None], force: bool=False) -> None:
		"""
		Tries writing to file using `writer`.
		Does not over-write files unless `force` is set to `True` and removes the file if an error occured while writing.

		Parameters
		----------
		writer : Callable[[TextIOWrapper], None]
			| a callable object to be executed when file is opened, takes one parameter (TextIOWrapper) representing the file to be written
		force : bool, default=`False`
			| whether to force over-writing the file
		"""

		if not self.exists() or force:
			with open(self._path, "w", encoding="utf-8") as file:
				writer(file)
	

	def read(self, reader: Callable[[TextIOWrapper], Any]) -> Any:
		"""
		Tries reading the file using `reader`.

		Parameters
		----------
		reader : Callable[[TextIOWrapper], Any]
			| a callable object to be executed when file is opened, the output of which will then be returned

		Returns
		-------
		Any
			| output of `reader`

		Raises
		------
		RuntimeError
			| when trying to read a non-existent file
		"""

		if not self.exists():
			raise RuntimeError("File cannot be read, as it does not exist")

		with open(self._path, "r", encoding="utf-8") as file:
			return reader(file)


	def remove(self) -> None:
		"""
		Delete the file if it exists.
		"""

		if self.exists():
			os.remove(self._path)


class HTMLFile(File):
	def __init__(self, dir: Directory, filename: str) -> None:
		"""
		HTMLFile initialiser.

		Parameters
		----------
		dir : Directory
			| a Directory type representing where the file will be stored
		filename : str
			| name of the file without '.html'
		"""

		super().__init__(dir, filename + ".html")
		
	
	def __str__(self) -> str:
		return f"<HTMLFile path={self._path}>"


	def write_html(
		self,
		html: str,
		force: bool=False,
		writer: Callable[[TextIOWrapper], None] | None=None
	) -> None: # break arguments into seperate lines to avoid line being to long
		"""
		Write the given HTML to the file.
		Does not over-write unless `force` is set to `True`.
		If a custom `writer` is supplied, `html` is ignored and only `writer` is executed.

		Parameters
		----------
		html : str
			| HTML code to write
		force : bool, default=`False`
			| whether to force over-writing the file
		writer : Callable[[TextIOWrapper], None], optional
			| a callable object to be executed when file is opened, takes one parameter (TextIOWrapper) representing the file to be written 
		"""

		if writer is None:
			def custom_writer(file: TextIOWrapper) -> None:
				file.write(html)
			writer = custom_writer

		self.write(writer, force=force)


	def read_html(self, reader: Callable[[TextIOWrapper], Any] | None=None) -> Any:
		if reader is None:
			def custom_reader(file: TextIOWrapper) -> str:
				return file.read()
			reader = custom_reader

		return self.read(reader)


class CSVFile(File):
	delimiter: str
	quotechar: str

	def __init__(self, dir: Directory, filename: str, delimiter: str=",", quotechar: str='"') -> None:
		""""
		CSVFile initialiser.

		Parameters
		----------
		dir : Directory
			| a Directory type representing where the file will be stored
		filename : str
			| name of the file without '.csv'
		delimiter : str, default=`","`
			| delimiter to seperate the CSV values
		quotechar : str, default=`'"'`
			| character to use for quotes
		"""

		super().__init__(dir, filename + ".csv")
		
		self.delimiter = delimiter
		self.quotechar = quotechar

	
	def __str__(self) -> str:
		return f"<CSVFile path={self._path}>"


	def write_rows(
		self,
		rows: Iterable[Iterable[str]],
		force: bool=False,
		writer: Callable[[TextIOWrapper], None] | None=None
	) -> None: # break arguments into seperate lines to avoid line being to long
		"""
		Write given rows to CSV file.
		Does not over-write unless `force` is set to `True`.
		If a custom `writer` is supplied, `rows` is ignored and only `writer` is executed.

		Parameters
		----------
		rows : Iterable[Iterable[str]]
			| an iterable containing rows to be written, represented as iterables of strings
		force : bool, default=`False`
			| whether to force over-writing the file
		writer : Callable[[TextIOWrapper], None], optional
			| a callable object to be executed when file is opened, takes one parameter (TextIOWrapper) representing the file to be written 
		"""

		if writer is None:
			def custom_writer(file: TextIOWrapper) -> None:
				# typing ignored due to weird csv._writer type being inaccessible
				csv_writer = csv.writer(file, delimiter=self.delimiter, quotechar=self.quotechar, quoting=csv.QUOTE_MINIMAL)  # type: ignore
				csv_writer.writerows(rows)
			writer = custom_writer

		self.write(writer, force=force)


	def write_columns(
		self,
		columns: Iterable[Iterable[str]],
		force: bool=False,
		writer: Callable[[TextIOWrapper], None] | None=None
	) -> None: # break arguments into seperate lines to avoid line being to long
		"""
		Write given columns to CSV file.
		If columns do not hold the same amount of values, will write smallest length column values per column.
		Does not over-write unless `force` is set to `True`.
		If a custom `writer` is supplied, `rows` is ignored and only `writer` is executed.

		Parameters
		----------
		columns : Iterable[Iterable[str]]
			| an iterable containing columns to be written, represented as iterables of strings
		force : bool, default=`False`
			| whether to force over-writing the file
		writer : Callable[[TextIOWrapper], None], optional
			| a callable object to be executed when file is opened, takes one parameter (TextIOWrapper) representing the file to be written 
		"""

		rows: Iterable[Iterable[str]] = zip(*columns) # columns to rows iterable
		self.write_rows(rows, force=force, writer=writer)


class JSONFile(File):
	def __init__(self, dir: Directory, filename: str) -> None:
		""""
		JSONFile initialiser.

		Parameters
		----------
		dir : Directory
			| a Directory type representing where the file will be stored
		filename : str
			| name of the file without '.json'
		"""

		super().__init__(dir, filename + ".json")

	
	def __str__(self) -> str:
		return f"<JSONFile path={self._path}>"


	# yes this is ugly and awful!
	JSONAccepted = dict["JSONAccepted", "JSONAccepted"] | list["JSONAccepted"] | tuple["JSONAccepted"] | str | int | float | bool | None
	def write_json(
		self,
		json_data: JSONAccepted,
		force: bool=False,
		writer: Callable[[TextIOWrapper], None] | None=None
	) -> None:
		"""
		Write given columns to JSON file.
		Does not over-write unless `force` is set to `True`.
		If a custom `writer` is supplied, `rows` is ignored and only `writer` is executed.

		Parameters
		----------
		columns : JSONAccepted
			| an object made up of only the types accepted by json library
		force : bool, default=`False`
			| whether to force over-writing the file
		writer : Callable[[TextIOWrapper], None], optional
			| a callable object to be executed when file is opened, takes one parameter (TextIOWrapper) representing the file to be written 
		"""

		if writer is None:
			def custom_writer(file: TextIOWrapper):
				json.dump(json_data, file)
			writer = custom_writer

		self.write(writer, force=force)
