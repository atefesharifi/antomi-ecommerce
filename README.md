# antomi-ecommerce
this is ecommerce website that write with django.
this project consist four app:
-home: for basic page such as home and see all products,filter products , ...
-accounts: for manage user account,login,register, ...
-cart: for shopping part of user account
-order: for complete user information that after that user can pay money for her/his shopping


It is suggested to have a dedicated virtual environment for each Django project, and one way to manage a virtual environment is venv, which is included in Python.

With venv, you can create a virtual environment by typing this in the command prompt, remember to navigate to where you want to create your project:


Windows:
py -m venv myproject

Unix/MacOS:
python -m venv myproject

This will set up a virtual environment, and create a folder named "myproject" with subfolders and files, like this:
myproject
  Include
  Lib
  Scripts
  pyvenv.cfg

Then you have to activate the environment, by typing this command:

Windows:
myproject\Scripts\activate.bat

Unix/MacOS:
source myproject/bin/activate

Once the environment is activated, you will see this result in the command prompt:

Windows:
(myproject) C:\Users\Your Name>

Unix/MacOS:
(myproject) ... $


then install all package that using in this program with this code:
pip install -r requirements.txt
