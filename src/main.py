def main():
    import ttkbootstrap as ttk
    from gui.main_window import MainWindow

    # Create the main window with modern theme
    root = ttk.Window(themename="cosmo")
    app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()