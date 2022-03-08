<p align="center">
<img src="https://user-images.githubusercontent.com/11627845/157017285-21dd8b01-e3c0-4812-8695-68f06664cc87.png" alt="Jina NOW logo: The data structure for unstructured data" width="150px">
<br>
(placeholder - design is working on the real logo)

<b>Democratization of neural search. Bootstrap your search case within minutes.</b>
</p>


<p align=center>
<a href="https://pypi.org/project/jina-now/"><img src="https://github.com/jina-ai/jina/blob/master/.github/badges/python-badge.svg?raw=true" alt="Python 3.7 3.8 3.9 3.10" title="Jina NOW supports Python 3.7 and above"></a>
<a href="https://pypi.org/project/jina-now/"><img src="https://img.shields.io/pypi/v/jina-now?color=%23099cec&amp;label=PyPI&amp;logo=pypi&amp;logoColor=white" alt="PyPI"></a>
</p>

<!-- start elevator-pitch -->

NOW gives the World access to customized neural search.
Data privacy became more important in recent years. 
Since most of the global data is private, public search engines can not be considered.
Furthermore, NOW fulfills the need of use-case-specific requirements.


🔒 **Private Data**: create your own search engine with privat data

🌐 **Democratization of Neural Search**: empowers everyone to use neural search - even people who noramlly would not have access to AI

🔋 **Batteries included**: simple deaults allow you to just provide the data and get your search case up and running

## Quick start
### Docker
One line to host them all.
```bash
docker run -it --rm \
--name jina-now \
--network="host" \
-v /var/run/docker.sock:/var/run/docker.sock \
-v $HOME/.kube:/root/.kube \
-v $PWD/jina-now:/root/data \
jinaaitmp/now:0.0.1
```

### Pip
```bash
pip install jina-now
(TBD)
```

## Supported Modalities
- [x] text
- [x] image
- [ ] audio
- [ ] 3d
- [ ] pdf 
- [ ] ...

## Examples

### Fashion
<img width="400" alt="image" src="https://user-images.githubusercontent.com/11627845/157079335-8f36fc73-d826-4c0a-b1f3-ed5d650a1af1.png">

### Chest X-Ray
<img src="https://user-images.githubusercontent.com/11627845/157067695-59851a77-5c43-4f68-80c4-403fec850776.png" width="400">

### NFT - bored apes
<img src="https://user-images.githubusercontent.com/11627845/157019002-573cc101-e23b-4020-825c-f37ec66c6ccf.jpeg" width="400">

### Art
<img width="400" alt="image" src="https://user-images.githubusercontent.com/11627845/157074453-721c0f2d-3f7d-4839-b6ff-bbccbdba2e5f.png">

### Cars
<img width="400" alt="image" src="https://user-images.githubusercontent.com/11627845/157081047-792df6bd-544d-420c-b180-df824c802e73.png">

### Street view
<img width="400" alt="image" src="https://user-images.githubusercontent.com/11627845/157087532-46ae36a2-c97f-45d7-9c3e-c624dcf6dc46.png">

### Birds
<img width="400" alt="image" src="https://user-images.githubusercontent.com/11627845/157069954-615a5cb6-dda0-4a2f-9442-ea807ad4a8d5.png">

### Now use your custom data :)