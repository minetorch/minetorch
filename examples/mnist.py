import sys

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from minetorch.miner import Miner
from minetorch.metrics import MultiClassesClassificationMetricWithLogic
from minetorch.spreadsheet import GoogleSheet
from torchvision import datasets, transforms

import socket
import socks
socks.set_default_proxy(socks.SOCKS5, "proxy.featurize.cn", 38080)
socket.socket = socks.socksocket


# step 1: define some model
class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(1, 10, kernel_size=5)
        self.conv2 = nn.Conv2d(10, 20, kernel_size=5)
        self.conv2_drop = nn.Dropout2d()
        self.fc1 = nn.Linear(320, 50)
        self.fc2 = nn.Linear(50, 10)

    def forward(self, x):
        x = F.relu(F.max_pool2d(self.conv1(x), 2))
        x = F.relu(F.max_pool2d(self.conv2_drop(self.conv2(x)), 2))
        x = x.view(-1, 320)
        x = F.relu(self.fc1(x))
        x = F.dropout(x, training=self.training)
        x = self.fc2(x)
        return F.log_softmax(x, dim=1)


# step 2: create dataloader
train_loader = torch.utils.data.DataLoader(
    datasets.MNIST('./data', train=True, download=True,
                   transform=transforms.Compose([
                       transforms.ToTensor(),
                       transforms.Normalize((0.1307,), (0.3081,))
                   ])),
    batch_size=256, shuffle=True)

val_loader = torch.utils.data.DataLoader(
    datasets.MNIST('./data', train=False, transform=transforms.Compose([
                       transforms.ToTensor(),
                       transforms.Normalize((0.1307,), (0.3081,))
                   ])),
    batch_size=256, shuffle=True)

# step 3: start to train, pay attension to the parameters of Miner
model = Net()

trainer = Miner(
    alchemistic_directory='./alchemistic_directory',
    code="Experiment-1",
    model=model,
    optimizer=optim.SGD(model.parameters(), lr=0.01),
    train_dataloader=train_loader,
    val_dataloader=val_loader,
    loss_func=torch.nn.CrossEntropyLoss(),
    drawer='matplotlib',
    plugins=[
        MultiClassesClassificationMetricWithLogic()
    ],
    sheet=GoogleSheet('1SkS1NWdn1gyrSTbtDRCFUeEsE8dHBJkH0W391bOIGB4', 'quickstart.json'),
    accumulated_iter=5
)

trainer.train()
