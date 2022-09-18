// UndoBuffer.h

#ifndef UNDOBUFFER_H
#define UNDOBUFFER_H
#include "PageData.h"
#include <QMetaType>
#include <QDebug>

#define MAX_UNDO 5

class UndoBuffer
{
public:
    UndoBuffer() {}
    ~UndoBuffer() {}

    // Add current page to undo list
    void pushImage(PageData &page)
    {
        if (page.isNull())
            return;
        m_undoState.insert(0, page);
        if (m_undoState.count() > MAX_UNDO)
            m_undoState.takeLast();
        while (!m_redoState.isEmpty())
            m_redoState.takeFirst();
    }

    // Rollback one change
    PageData undoEdit(PageData &page)
    {
        if (page.isNull())
            return page;
        if (m_undoState.count() > 0)
        {
            m_redoState.insert(0, page);
            return m_undoState.takeFirst();
        }
        else
            return page;
    }

    // Reapply previous undo
    PageData redoEdit(PageData &page)
    {
        if (page.isNull())
            return page;
        if (m_redoState.count() > 0)
        {
            m_undoState.insert(0, page);
            return m_redoState.takeFirst();
        }
        else
            return page;
    }
 

private:
    QList<PageData> m_undoState;
    QList<PageData> m_redoState;
};

Q_DECLARE_METATYPE(UndoBuffer)
#endif // UNDOBUFFER_H