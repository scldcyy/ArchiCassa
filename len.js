getPathLen()
function getPathLen(id='#lineABC')
{
    // var path = document.querySelector('#lineABC');
    var paths = document.getElementsByTagName("path");
    // var path= document.createElementNS('http://www.w3.org/2000/svg','path');
    // path.setAttribute("d","M 430 360 l 380 100 l 70 10 l 98 108 l 107 99 l 95 92");
    var lenArr=[];
    for (var i=0;i<paths.length;i++)
    {
        lenArr.push(paths[i].getTotalLength());
    }
    console.log(lenArr);
    // var content = JSON.stringify(lent);
    // // 创建一个a链接dom
    // var dom_a = document.createElement('a');
    // // 设置保存的json文件名称
    // dom_a.download = 'C:/Users/85365/PycharmProjects/ArchiCasca/jjj.json';
    // // 设置文件保存的内容
    // dom_a.href = 'data:text/plain;charset=utf-8,' + encodeURIComponent(content);
    // // 添加a链接dom
    // document.body.appendChild(dom_a);
    // // 点击触发a链接
    // dom_a.click();
    // // 删除a链接dom
    // document.body.removeChild(dom_a);
    }
