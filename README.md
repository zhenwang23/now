<p align="center">
<img src="https://user-images.githubusercontent.com/11627845/160392052-69672e7f-2e4d-45ee-a617-4384256bb6e8.jpg" alt="Jina NOW logo: The data structure for unstructured data" width="300px">
<br>

<b>One line to host them all. Bootstrap your search case in minutes.</b>
</p>

<p align=center>
<a href="https://pypi.org/project/jina-now/"><img src="https://github.com/jina-ai/jina/blob/master/.github/badges/python-badge.svg?raw=true" alt="Python 3.7 3.8 3.9 3.10" title="Jina NOW supports Python 3.7 and above"></a>
<a href="https://pypi.org/project/jina-now/"><img src="https://img.shields.io/pypi/v/jina-now?color=%23099cec&amp;label=PyPI&amp;logo=pypi&amp;logoColor=white" alt="PyPI"></a>
</p>

<!-- start elevator-pitch -->

NOW gives the world access to customized neural search in just one line of code.

Data privacy is becoming increasingly important. And with most data being private, you can't use public search engines (like Google) to search for it. This is where Jina NOW comes in, letting you build a search engine for your private data with just one terminal command.

- 🔒 **Private data**: Create your own search engine with your own private data
- 🌐 **Democratization of neural search**: Empowers everyone to use neural search - even people who wouldn't normally have access to AI
- 🔋 **Batteries included**: simple defaults allow you to provide just the data and get your search use case up and running

### Pip
```bash
pip install jina-now
```
In case you need sudo for running Docker, install and use jina-now using sudo as well.
### Usage
```bash
jina-now --data [pushpullid | localpath | url] --quality [medium | good | excellent] --cluster [k8s-cluster-name]
```

### quick start
```bash
jina-now start
```
### parameters
```bash
jina-now start --quality medium --data /local/img/folder
```
### Cleanup
```bash
jina-now stop
```

## Supported Modalities (more will be added)

- [x] Text
- [x] Image
- [ ] Audio
- [ ] Video
- [ ] 3D mesh
- [ ] PDF 
- [ ] ...

## Examples

### Fashion

Fine-tuned on category, gender and product variant
<br>
<img width="400" alt="image" src="https://user-images.githubusercontent.com/11627845/157079335-8f36fc73-d826-4c0a-b1f3-ed5d650a1af1.png">

### Chest X-Ray

Fine-tuned on diagnoses given by doctors
<br>
<img src="https://user-images.githubusercontent.com/11627845/157067695-59851a77-5c43-4f68-80c4-403fec850776.png" width="400">

### NFT - bored apes

Fine-tuned on the attributes of the Apes
<br>
<img src="https://user-images.githubusercontent.com/11627845/157019002-573cc101-e23b-4020-825c-f37ec66c6ccf.jpeg" width="400">

### Art

Fine-tuned on the art genre
<br>
<img width="400" alt="image" src="https://user-images.githubusercontent.com/11627845/157074453-721c0f2d-3f7d-4839-b6ff-bbccbdba2e5f.png">

### Cars

Color invariant fine-tuning on the car model
<br>
<img width="400" alt="image" src="https://user-images.githubusercontent.com/11627845/157081047-792df6bd-544d-420c-b180-df824c802e73.png">

### Street view

Fine-tuned on country classification
<br>
<img width="400" alt="image" src="https://user-images.githubusercontent.com/11627845/157087532-46ae36a2-c97f-45d7-9c3e-c624dcf6dc46.png">

### Birds

Fine-tuned on bird species
<br>
<img width="400" alt="image" src="https://user-images.githubusercontent.com/11627845/157069954-615a5cb6-dda0-4a2f-9442-ea807ad4a8d5.png">

### Now use your custom data :)
