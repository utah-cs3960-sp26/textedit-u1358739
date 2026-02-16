Command to run coverage: pytest --cov=main

I achieved 96% test coverage

List of uncovered code:
Lines 2425-2446  This is the code for openning a file with unsupported encoding.  In order to test this I would have to create a file with invalid UTF-8 bytes.

Lines 2402-2407  This code is again testing for an encoding error.

Lines 2501-2509  This code is for a feature that merges directories if they are in the same place and have the same name.  This is not tested becuase it requires a complex file structure to test.

Line 2518-2544  This is the code for catching errors when the user is trying to drag and drop a file.  This is untested because it would require timing a file error while it is being dragged.

Line 2828-2829  This is the code for catching an exception when trying to find something.  This isn't tested because it is hard to create an exception when trying to find something.

Line 3032-3034  This is the code that runs when a user chooses to save after trying to close, but the save fails.  This isn't tested because it is really hard to set up this senario.

Line 3042-3046  This is the main function entry point.  This isn't tested because my tests don't actually call the main function.  They create the TextEditor directly.

Line 2078-2084  This is the code for closing a file that also triggers closing a view panel when the file also needs saved.  This isn't tested because it is very complex to set up.