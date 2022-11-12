#ifndef BOOKMARKS_H
#define BOOKMARKS_H

#include <QWidget>
#include <QListWidget>
#include "PageData.h"

class Bookmarks : public QListWidget
{
    Q_OBJECT

public:
    Bookmarks(QWidget * parent = NULL);
    ~Bookmarks();
    int blurRadius = 5;

public slots:
    void openFiles();
    void insertFiles();
    void replaceFiles();
    void toGrayscale();
    void setBlurRadius(int val);
    void toBinary();
    void saveFiles();
    void saveToDir();
    bool anyModified();
    void selectEven();
    void selectOdd();
    void deleteSelection();
    void rotateCW();
    void rotateCCW();
    void rotate180();
    void mirrorHoriz();
    void mirrorVert();
    void updateIcon();

signals:
    void progressSig(QString descr, int val);
    void updateViewerSig();

private:
    void readFiles(QString cmd);
    bool saveCommon(QListWidgetItem* itemPtr, QString &fileName, QString &backupName);
    void rotateSelection(int val);
    void mirrorSelection(int dir);
    QIcon makeIcon(PageData &image, bool flag);
};

#endif
