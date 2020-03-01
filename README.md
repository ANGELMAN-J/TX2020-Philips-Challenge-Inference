# TX2020 Philips Challenge Inference
This repo contains a finetuned CNN and a script for easy inference.

### Instructions
0. install dependencies by either A) using the 'requirements.txt' or B) using the docker image.
1. place new images in the folder 'VALIDATION_IMAGES/'. Note that images must not be in subfolders.
2. run inference.py
3. wait for the script to run - it'll keep you in the loop as to what it is currently doing.
4. the results will be shown in the script output as well as in a file called 'validation_output.txt'. 
This file is formatted to comply with the instructions, thus no confidence etc. is provided.

Please not that the code is written to take advantage of a GPU, if it is available, and use the CPU otherwise. 
If this creates issues (there is a small chance that on MAC the specified pytorch version might have trouble with cuda),
just replace line 20 in inference.py with "device = torch.device('cpu')".

Additionally, since solutions have to be shared to github, and github limits files to be <100MB, I split the model weights
into chunks using the code in "split_stitch.py" which is then stitched together the first time "inference.py" is run. 
This should work without issue, but in case there is a problem, please contact me so I can provide a direct download link
to the model on gDrive.

Finally, if you don't have any images of the four applicances ready, you can try out the code with the images 
in "EXAMPLE_VALIDATION_IMAGES/". Just copy them to "VALIDATION_IMAGES/" and run inference.py. Note that 3/4 of those images
were used for training, so they do not reflect the model performance accurately.

### Challenge
Detailed information [can be found here](https://brainporteindhoven.com/int/techxperience/challenges/philips/) but in 
a nutshell, 20 images each of 4 philips appliances were provided as a training set to create an algorithm that can 
identify them on new photos. Each picture contains exactly on product and the products are at different angles, 
appear in front of different backgrounds in different parts of the pictures, and take up varying amounts of space.

According to the material provided, the results will be evaluated in terms of accuracy (and not say, log_loss or AUC),
and limitless image augmentation was allowed.

### Approach
I decided to finetune a cnn pre-trained on imagenet. I tested a few vgg and resnet versions and VGG11 with batchnorm 
performed best on the validation data. With the help of google images, I added a few extra images per class.
Then I split off a held-out test set, and trained with a train/validation split.

For training, I added heavy image augmentation to the train set, and finetuned the cnn in multiple phases.
In the first phase, the last fully connected layer was trained while the rest of the network was frozen. 
Then, progressively  the other fully connected layers were added. Next, the last block of the vgg16 was progressively trained.
And finally both the last block and the fully connected layers were trained together.

According to my test-set, this approach seemed to be surprisingly effective. 
<p float="left">
  <img src="Model performance test set.png" width="750" />
</p>
However, it appears that the background can often throw the model off. For instance, round features make the model 
think that it sees the bottle. Some of the strategies I discuss below might have been effective to mitigate this.

### Further thoughts
The current approach seems to work well according to my test set. There were many cool ideas that I didn't pursue 
due to the small data set size, like 1.; approach 2. that would be possible but that I think verge on cheating,
approach 3./4. due to computational and storage constraints I had.
#### 1. Detection -> recognition
Given the provided training images, we would expect that the objects in question might only make up a small part of the 
images and that they can appear in any location. Thus, finding the most interesting candidate regions first and then
running a classification network on them might be more effective. However, I think such approaches would have required
much more data. [A paper that pursues such an approach for medical images can be found here](https://arxiv.org/abs/2002.07613), 
but they used more than 1 million images. 
#### 2. Massive image augmentation
Generally, whoever did the most image augmentation will likely win the challenge. It would have been possible, for in-
stance to buy all four appliances and take a few dozen or hundred of pictures each; or to exhaustively search the internet.
#### 3. Smart, automated image augmentation
Relatedly, since the products always look the same, it would have been possible to use the training 
images to cut out all the products and put them on a transparent background. Then, one could have written a script to 
take random background images (i.e. Imagenet, random google searches etc.) and impose the products on them, plus adding
a bit of noise to the product image to prevent overfitting.
#### 4. Use crossvalidation instead of train-val-test-split /  create an ensemble
Those strategies would have been also quite effective but given the file size restrictions of github, and my computational constraints,
I had to forgo them.
