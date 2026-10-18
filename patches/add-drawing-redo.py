#!/usr/bin/env python3
"""Add session-local freehand redo to an upstream Sioyek source checkout."""
from pathlib import Path
import sys

root = Path(sys.argv[1]) / 'pdf_viewer'


def edit(name, replacements):
    path = root / name
    source = path.read_text()
    for old, new in replacements:
        if new in source:
            continue
        if source.count(old) != 1:
            raise RuntimeError(f'Upstream changed: review {name}: {old!r}')
        source = source.replace(old, new, 1)
    path.write_text(source)


edit('document.h', [
    ('    std::map<int, std::vector<FreehandDrawing>> page_freehand_drawings;',
     '    std::map<int, std::vector<FreehandDrawing>> page_freehand_drawings;\n'
     '    std::vector<std::pair<int, FreehandDrawing>> undone_freehand_drawings;'),
    ('    void undo_freehand_drawing();',
     '    void undo_freehand_drawing();\n    void redo_freehand_drawing();'),
])
edit('document.cpp', [
    ('        page_freehand_drawings[docpos.page].push_back(new_drawing);',
     '        undone_freehand_drawings.clear();\n'
     '        page_freehand_drawings[docpos.page].push_back(new_drawing);'),
    ('        page_freehand_drawings[most_recent_page_index].pop_back();',
     '        undone_freehand_drawings.emplace_back(most_recent_page_index,\n'
     '            page_freehand_drawings[most_recent_page_index].back());\n'
     '        page_freehand_drawings[most_recent_page_index].pop_back();'),
    ('const std::vector<FreehandDrawing>& Document::get_page_drawings(int page) {',
     '''void Document::redo_freehand_drawing() {
    std::lock_guard<std::mutex> lock(drawings_mutex);
    if (undone_freehand_drawings.empty()) return;
    const auto& undone = undone_freehand_drawings.back();
    page_freehand_drawings[undone.first].push_back(undone.second);
    undone_freehand_drawings.pop_back();
    is_drawings_dirty = true;
}

const std::vector<FreehandDrawing>& Document::get_page_drawings(int page) {'''),
    ('void Document::delete_all_page_drawings(int page) {',
     'void Document::delete_all_page_drawings(int page) {\n    undone_freehand_drawings.clear();'),
    ('void Document::delete_all_drawings() {',
     'void Document::delete_all_drawings() {\n    undone_freehand_drawings.clear();'),
    ('void Document::delete_page_intersecting_drawings(int page, AbsoluteRect absolute_rect, bool mask[26]) {',
     'void Document::delete_page_intersecting_drawings(int page, AbsoluteRect absolute_rect, bool mask[26]) {\n    undone_freehand_drawings.clear();'),
    ('void Document::load_drawings() {',
     'void Document::load_drawings() {\n    undone_freehand_drawings.clear();'),
])
edit('main_widget.h', [
    ('    void handle_undo_drawing();',
     '    void handle_undo_drawing();\n    void handle_redo_drawing();'),
])
edit('main_widget.cpp', [
    ('void MainWidget::handle_undo_drawing() {',
     '''void MainWidget::handle_redo_drawing() {
    if (!doc()) return;
    doc()->redo_freehand_drawing();
    invalidate_render();
}

void MainWidget::handle_undo_drawing() {'''),
])
edit('input.cpp', [
    ('class UndoDrawingCommand : public Command {',
     '''class RedoDrawingCommand : public Command {
public:
    static inline const std::string cname = "redo_drawing";
    static inline const std::string hname = "Redo freehand drawing";
    RedoDrawingCommand(MainWidget* w) : Command(cname, w) {};
    void perform() { widget->handle_redo_drawing(); }
    bool requires_document() { return true; }
};

class UndoDrawingCommand : public Command {'''),
    ('    register_command<UndoDrawingCommand>();',
     '    register_command<UndoDrawingCommand>();\n    register_command<RedoDrawingCommand>();'),
])
