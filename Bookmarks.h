#ifndef BOOKMARKS_H
#define BOOKMARKS_H

#include <QWidget>
#include <QListWidget>

class Bookmarks : public QListWidget
{
    Q_OBJECT

public:
    Bookmarks(QWidget * parent = NULL);
    ~Bookmarks();

public slots:
    void readFiles();
    void saveFiles();
    void saveAsFiles();
    void createTIFF();

signals:
    void progressSig(QString descr, int val);

private:
    QIcon makeIcon(QImage image, bool flag);
};

#endif