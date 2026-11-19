#include <linux/init.h>
#include <linux/module.h>
#include <linux/miscdevice.h>
#include <linux/fs.h>
#include <linux/uaccess.h>

static const char message[] = "hello from pr14\n";

static ssize_t demo_read(struct file *file, char __user *buffer, size_t length, loff_t *offset) {
    return simple_read_from_buffer(buffer, length, offset, message, sizeof(message) - 1);
}

static const struct file_operations demo_fops = {
    .owner = THIS_MODULE,
    .read = demo_read,
};

static struct miscdevice demo_device = {
    .minor = MISC_DYNAMIC_MINOR,
    .name = "pr14demo",
    .fops = &demo_fops,
    .mode = 0444,
};

static int __init demo_init(void) { return misc_register(&demo_device); }
static void __exit demo_exit(void) { misc_deregister(&demo_device); }

module_init(demo_init);
module_exit(demo_exit);
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Учебное символьное устройство ПР-14");
