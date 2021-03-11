import torch.optim as optim
import torch
import torch.nn as nn
import torch.utils.data
import torch.backends.cudnn as cudnn
import torchvision
from torchvision import transforms as transforms
from torch.cuda.amp import autocast as autocast
from torch.cuda.amp import GradScaler as GradScaler
import time
import numpy as np
from CNNmodels import *

CLASSES = ('plane', 'car', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck')

class CNN(object):
    def __init__(self):
        self.model = None
        self.lr = 0.001
        self.epochs = 20
        self.train_batch_size = 100
        self.test_batch_size = 100
        self.criterion = None
        self.optimizer = None
        self.scheduler = None
        self.device = None
        self.cuda = torch.cuda.is_available()
        self.train_loader = None
        self.test_loader = None
        self.scaler = None
    
    def load_data(self):
        train_transform = transforms.Compose([transforms.RandomHorizontalFlip(), transforms.ToTensor()])
        test_transform = transforms.Compose([transforms.ToTensor()])
        train_set = torchvision.datasets.CIFAR10(root='./data', train=True, download=True, transform=train_transform)
        self.train_loader = torch.utils.data.DataLoader(dataset=train_set, batch_size=self.train_batch_size, shuffle=True)
        test_set = torchvision.datasets.CIFAR10(root='./data', train=False, download=True, transform=test_transform)
        self.test_loader = torch.utils.data.DataLoader(dataset=test_set, batch_size=self.test_batch_size, shuffle=False)

    def load_model(self):
        if self.cuda:
            self.device = torch.device('cuda')
            cudnn.benchmark = True
        else:
            self.device = torch.device('cpu')

        # self.model = LeNet().to(self.device)
        self.model = AlexNet().to(self.device)
        # self.model = VGG11().to(self.device)
        # self.model = VGG13().to(self.device)
        # self.model = VGG16().to(self.device)
        # self.model = VGG19().to(self.device)
        # self.model = GoogLeNet().to(self.device)
        # self.model = resnet18().to(self.device)
        # self.model = resnet34().to(self.device)
        # self.model = resnet50().to(self.device)
        # self.model = resnet101().to(self.device)
        # self.model = resnet152().to(self.device)
        # self.model = DenseNet121().to(self.device)
        # self.model = DenseNet161().to(self.device)
        # self.model = DenseNet169().to(self.device)
        # self.model = DenseNet201().to(self.device)
        # self.model = WideResNet(depth=28, num_classes=10).to(self.device)

        self.optimizer = optim.Adam(self.model.parameters(), lr=self.lr)
        self.scheduler = optim.lr_scheduler.MultiStepLR(self.optimizer, milestones=[75, 150], gamma=0.5)
        self.criterion = nn.CrossEntropyLoss().to(self.device)
        self.scaler = GradScaler()

    def train(self):
        print("train:")
        self.model.train()
        train_loss = 0
        train_correct = 0
        total = 0

        for batch_num, (data, target) in enumerate(self.train_loader):
            data, target = data.to(self.device), target.to(self.device)
            self.optimizer.zero_grad()

            # output = self.model(data)
            # loss = self.criterion(output, target)
            # loss.backward()
            # self.optimizer.step()
            
            # Runs the forward pass with autocasting.
            with autocast():
              output = self.model(data)
              loss = self.criterion(output, target)
            self.scaler.scale(loss).backward()
            self.scaler.step(self.optimizer)
            self.scaler.update()

            train_loss += loss.item()
            prediction = torch.max(output, 1)  # second param "1" represents the dimension to be reduced
            total += target.size(0)

            # train_correct incremented by one if predicted right
            train_correct += np.sum(prediction[1].cpu().numpy() == target.cpu().numpy())

            # progress_bar(batch_num, len(self.train_loader), 'Loss: %.4f | Acc: %.3f%% (%d/%d)'
            #             % (train_loss / (batch_num + 1), 100. * train_correct / total, train_correct, total))

            # print('Loss: %.4f | Acc: %.3f%% (%d/%d)'
            #         % (train_loss / (batch_num + 1), 100. * train_correct / total, train_correct, total))

        return train_loss, train_correct / total

    def test(self):
        print("test:")
        self.model.eval()
        test_loss = 0
        test_correct = 0
        total = 0

        with torch.no_grad():
            for batch_num, (data, target) in enumerate(self.test_loader):
                data, target = data.to(self.device), target.to(self.device)
                output = self.model(data)
                loss = self.criterion(output, target)
                test_loss += loss.item()
                prediction = torch.max(output, 1)
                total += target.size(0)
                test_correct += np.sum(prediction[1].cpu().numpy() == target.cpu().numpy())

                # progress_bar(batch_num, len(self.test_loader), 'Loss: %.4f | Acc: %.3f%% (%d/%d)'
                #              % (test_loss / (batch_num + 1), 100. * test_correct / total, test_correct, total))
                # print('Loss: %.4f | Acc: %.3f%% (%d/%d)'
                #     % (test_loss / (batch_num + 1), 100. * test_correct / total, test_correct, total))

        return test_loss, test_correct / total

    # def save(self):
    #     model_out_path = "result.txt"
    #     torch.save(self.model, model_out_path)
    #     print("Checkpoint saved to {}".format(model_out_path))

    def run(self):
        self.load_data()
        self.load_model()
        accuracy = 0
        for epoch in range(1, self.epochs + 1):
            start = time.time()
            # self.scheduler.step()
            print("\n===> epoch: %d/%d" % (epoch, self.epochs))
            train_result = self.train()
            self.scheduler.step()
            end = time.time()
            print('Loss: %.4f | Acc: %.3f%%| time: %.3fs'
                % (train_result[0] / 501, 100. * train_result[1], end-start))
            if epoch == self.epochs:
              test_result = self.test()
              accuracy = max(accuracy, test_result[1])
              print("===> BEST ACC. PERFORMANCE: %.3f%%" % (accuracy * 100))
              #self.save()

# Defining main function 
def main():
    globelStart = time.time() 
       # parser = argparse.ArgumentParser(description="cifar-10 with PyTorch")
    # parser.add_argument('--lr', default=0.001, type=float, help='learning rate')
    # parser.add_argument('--epoch', default=200, type=int, help='number of epochs tp train for')
    # parser.add_argument('--trainBatchSize', default=100, type=int, help='training batch size')
    # parser.add_argument('--testBatchSize', default=100, type=int, help='testing batch size')
    # parser.add_argument('--cuda', default=torch.cuda.is_available(), type=bool, help='whether cuda is in use')
    # args = parser.parse_args()
    CNN1 = CNN()
    CNN1.run()
    print("total training time: %.3fs" % (time.time() - globelStart))

# Using the special variable  
# __name__ 
if __name__=="__main__": 
    main()