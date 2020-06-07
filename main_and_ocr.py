#modules from the python standard library
import os
from pathlib import Path
import re

#third party modules
from pdf2image import convert_from_path
from PIL import Image
from PyPDF2 import PdfFileMerger
import shutil

#py files downloaded from github
import pdf_redactor

cwd = Path(os.path.dirname(os.path.realpath(__file__)))
#set cwd equal to the folder that this file is currently in

final_folder = os.makedirs((cwd / Path("Processed Documents")), exist_ok = True)
#create a folder called "Processed Documents" in the same folder as above

img_exts = [".bmp", ".gif", ".jpg", ".jpeg", ".png", ".jp2", ".tif", ".tiff"]
#create a list of all the image file extensions

processed_documents = []
#create a list for all the processed documents

for entry in os.scandir(cwd):
#for files and folders (entries) in the cwd
    if entry.is_dir():
    #if the entry is a folder
        subfolder = entry.path
        #set subfolder equal to the path to the entry
        
        list_dir = os.listdir(subfolder)
        #set list_dir equal to the lists of files in the subfolders
        
        pdf_ims = []
        #create an empty list to store the pdfs of the individual pages
        
        if str(cwd / Path("Processed Documents")) in subfolder or str(cwd /Path("__pycache__")) in subfolder:
        #if the name of the subfolder is Processed Documents
            continue
            #don't act on the subfolder
        
        else:
        #otherwise
            for filename in list_dir:
            #for individual files within the lists of files
                for img_ext in img_exts:
                #for each extension in the list of img_exts
                    
                    if filename.lower().endswith(".pdf"):
                    #if the file has the pdf extension
                        
                        options = pdf_redactor.RedactorOptions()
                        #create an instance of RedactorOptions and set
                        #it equal to rdct_optns
                        
                        options.content_filters = [(re.compile(r"\w*|\d*|\s*"),lambda m : "")]
                        #set up a regex to find all text and replace
                        #it with nothing
                        
                        options.input_stream = open((subfolder + "/" + filename), "rb")
                        #set input_stream in options equal to the filename in read mode
                        #(the b is there because this is a binary file)

                        options.output_stream = open((subfolder + "/" + "no_text_" + filename), "wb")
                        #set output_stream in options equal to the filename (with _text_free in front
                        #of it) in write mode
                        #this is output file

                        pdf_redactor.redactor(options)
                        #perform the redactor method on
                        #rdct_optns 

                        options.input_stream.close()
                        #close the input_stream filename
                        
                        options.output_stream.close()
                        #close the output_stream filename

                        convert_from_path(
                        #convert each page from the output file into a png image
                            pdf_path = (subfolder + "/" + "no_text_" + filename), 
                            #convert the text_free pdf file into an image
                            output_folder = subfolder,
                            #put the image file in the subfolder
                            fmt = "tiff",
                            #make the image file a png file
                            output_file = (f"no_text_{filename}")
                            #name the new image file the filename with text_free_ in front of it
                            )
                        
                        im = Image.open(subfolder + "/" + filename)
                        #open the image file
                    
                        new_pdf_name = f"{filename}.pdf"
                        #set the new_pdf_name equal to the pdf version of the image file
                        
                        pdf_ims.append(new_pdf_name)
                        #add the pdf versions of the images to a list
                        
                        new_pdf = im.save(new_pdf_name)
                        #convert the image file to a pdf

                    elif filename.lower().endswith(img_ext):
                    #if the file has a listed image extension
                        im = Image.open(subfolder + "/" + filename)
                        #open the image file
                        
                        #TODO: rotate all the pages so they're facing the right way
                        #TODO: unwarp the page
                        #TODO: deskew the page (skip for cropped images)
                        #TODO: remove chromatic abberration from the page
                        #TODO: remove moire from the page
                        #TODO: contrast and color correction (might require some fanangling since 
                        #       they have requirements specific to Internet Archive) (also skip
                        #       color correction for images lacking color cards or other reference
                        #       points)
                        #TODO: evening exposure within each page
                        #TODO: evening exposure across all pages
                        
                        new_pdf_name = f"{filename}.pdf"
                        #set the new_pdf_name equal to the pdf version of the image file
                        
                        pdf_ims.append(new_pdf_name)
                        #add the pdf versions of the images to a list
                        
                        new_pdf = im.save(new_pdf_name)
                        #convert the image file to a pdf

                merger = PdfFileMerger()
                #set the merger variable equal to the function that merges pdf files
                
                for pdf in pdf_ims:
                #for each pdf file that represents an individual page
                    merger.append(pdf)
                    #add the pdf file to the list of files to be merged
                    
                
                final_file_name = f'FINAL_{Path(subfolder).name}.pdf'
                #set final_file_name equal to what will be the name for the complete pdf
                
                merger.write(final_file_name)
                #merge all the pdf files into a single pdf called whatever
                #final_file_name is equal to
                
                shutil.move(final_file_name, os.path.join((str(cwd) + "/" + "Processed Documents"), final_file_name))
                #move the final pdf to the Processed Documents folder
                
                merger.close()                 
                #close the pdf file
        
            for pdf in pdf_ims:
            #for each pdf file that represents an individual page
                os.unlink(pdf)
                #delete them, now that they've been merged
                #into a single document
                

#TODO: OCR on each pdf

#6/3/2020 - Open issue on github about tiffs not working